import os
from django.conf import settings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# Thêm thư viện để load file txt nếu chưa có index
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CẤU HÌNH ---
BASE_DIR = settings.BASE_DIR
FAISS_INDEX_DIR = BASE_DIR / "faiss_index"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

# ⚠️ THAY KEY CỦA BẠN VÀO ĐÂY
GROQ_API_KEY = ""

rag_chain = None

def load_vector_store():
    # Dùng model embeddings giống hệt file cũ để tương thích
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 1. Nếu đã có Index thì load lên
    if os.path.exists(FAISS_INDEX_DIR):
        print("--- [Groq] Đang tải FAISS Index từ đĩa... ---")
        return FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    
    # 2. Nếu chưa có thì tạo mới luôn (Phòng hờ lỗi file index thiếu)
    else:
        print("--- [Groq] Chưa thấy Index, đang tạo mới từ file txt... ---")
        if not os.path.exists(KNOWLEDGE_BASE_DIR):
             os.makedirs(KNOWLEDGE_BASE_DIR)
             # Tạo file mẫu nếu thư mục rỗng để tránh lỗi
             with open(os.path.join(KNOWLEDGE_BASE_DIR, "data.txt"), "w", encoding="utf-8") as f:
                 f.write("Thông tin khách sạn The Sailing Bay...")

        loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        documents = loader.load()
        if not documents:
            raise Exception("Thư mục knowledge_base không có file .txt nào!")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(texts, embeddings)
        vector_store.save_local(FAISS_INDEX_DIR)
        return vector_store

def initialize_chain():
    global rag_chain
    if rag_chain: return

    print("--- [Groq] Đang khởi tạo kết nối API... ---")
    
    if "gsk_" not in GROQ_API_KEY:
        raise ValueError("Lỗi: Bạn chưa điền GROQ_API_KEY trong file rag_pipeline_groq.py")

    try:
        # 1. Khởi tạo LLM
        llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY
        )

        # 2. Vector DB
        vector_store = load_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        # 3. Prompt
        template = """Bạn là nhân viên lễ tân ảo chuyên nghiệp và thân thiện của "The Sailing Bay Resort".

        HƯỚNG DẪN QUAN TRỌNG:
        1. ĐỒNG NHẤT KHÁI NIỆM: Nếu khách hàng dùng từ "khách sạn", "hotel", hay "chỗ nghỉ", hãy hiểu rằng họ đang nói về "The Sailing Bay Resort" (hoặc "Khu nghỉ dưỡng") được nhắc đến trong ngữ cảnh.
        2. NGUỒN DỮ LIỆU: Chỉ dựa vào thông tin được cung cấp trong phần "Ngữ cảnh" (Context) bên dưới để trả lời. Không được tự bịa ra thông tin bên ngoài.
        3. TRƯỜNG HỢP KHÔNG BIẾT: Nếu câu trả lời không có trong ngữ cảnh, hãy đáp: "Dạ xin lỗi quý khách, hiện tại em chưa có thông tin cụ thể về vấn đề này trong hệ thống ạ."
        4. THÁI ĐỘ: Luôn trả lời lễ phép, xưng "em" và gọi người dùng là "quý khách".

        Ngữ cảnh (Context):
        -------------------
        {context}
        -------------------

        Câu hỏi của khách (Question): {question}

        Câu trả lời (bằng Tiếng Việt):"""

        prompt = ChatPromptTemplate.from_template(template)

        # 4. Chain
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("--- [Groq] Đã sẵn sàng! ---")

    except Exception as e:
        print(f"--- [Groq] LỖI KHỞI TẠO: {e} ---")
        raise e

def get_chatbot_response(question):
    if not rag_chain:
        initialize_chain()
    return rag_chain.invoke(question)