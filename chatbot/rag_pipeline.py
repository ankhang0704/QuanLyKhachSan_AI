import os
from django.conf import settings

# --- CÁC THƯ VIỆN LOCAL ---
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # Dùng cái này thay Google
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Định nghĩa các đường dẫn
BASE_DIR = settings.BASE_DIR
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
FAISS_INDEX_DIR = BASE_DIR / "faiss_index"
# Đảm bảo tên file model khớp 100% với file bạn tải về
MODEL_PATH = os.path.join(settings.BASE_DIR, "models", "qwen1_5-1_8b-chat-q4_k_m.gguf")

# Biến toàn cục để giữ instance
rag_chain_instance = None

# --- HÀM 1: TẢI HOẶC TẠO VECTOR STORE (OFFLINE) ---
def load_vector_store():
    # Sử dụng model nhúng Offline (Miễn phí, chạy trên máy)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists(FAISS_INDEX_DIR):
        print("Đang tải Vector Store từ file (Offline)...")
        vector_store = FAISS.load_local(
            FAISS_INDEX_DIR, 
            embeddings, 
            allow_dangerous_deserialization=True 
        )
    else:
        print("Chưa có Vector Store. Đang tạo mới (Offline)...")
        # Đọc file .txt với encoding utf-8
        loader = DirectoryLoader(
            KNOWLEDGE_BASE_DIR, 
            glob="*.txt", 
            loader_cls=TextLoader, 
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        
        vector_store = FAISS.from_documents(texts, embeddings)
        vector_store.save_local(FAISS_INDEX_DIR)
        print(f"Đã tạo Vector Store tại {FAISS_INDEX_DIR}")
        
    return vector_store

# --- HÀM 2: KHỞI TẠO MODEL & CHAIN ---
def initialize_rag_chain():
    global rag_chain_instance
    if rag_chain_instance is not None:
        return rag_chain_instance

    print(f"Đang khởi tạo Local AI Model từ: {MODEL_PATH} ...")
    
    # Kiểm tra xem file model có tồn tại không
    if not os.path.exists(MODEL_PATH):
        print(f"LỖI: Không tìm thấy file model tại {MODEL_PATH}")
        return None

    try:
        # --- 2. KHỞI TẠO LLAMACPP (Thay thế CTransformers) ---
        # LlamaCpp tự động nhận diện model (Qwen, Llama, v.v.) nên không cần model_type
        llm = LlamaCpp(
            model_path=MODEL_PATH,
            temperature=0.3,
            max_tokens=512,
            n_ctx=1024,       # Độ dài ngữ cảnh
            top_p=1,
            verbose=True,     # Hiện log chi tiết để debug
            n_gpu_layers=0    # Để 0 nếu chạy CPU. Nếu có card rời NVIDIA, tăng lên (vd: 20)
        )
        # -----------------------------------------------------

        vector_store = load_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})  # Lấy 1 đoạn gần nhất

        # --- Tạo Prompt Template --- Hỗ trợ tiếng Việt
        template = """<|im_start|>system
        Bạn là nhân viên lễ tân của khách sạn The Sailing Bay.
        Nhiệm vụ: Trả lời câu hỏi của khách dựa trên thông tin được cung cấp (Context).
        
        YÊU CẦU BẮT BUỘC:
        1. Trả lời hoàn toàn bằng TIẾNG VIỆT.
        2. Văn phong: Thân thiện, ngắn gọn, xưng 'em' và gọi khách là 'quý khách'.
        3. Nếu thông tin không có trong Context, hãy nói: "Dạ em xin lỗi, hiện em chưa có thông tin về vấn đề này ạ."
        <|im_end|>
        <|im_start|>user
        Thông tin hỗ trợ (Context):
        {context}
        
        Câu hỏi của khách: {question}
        <|im_end|>
        <|im_start|>assistant
        """
        
        prompt = ChatPromptTemplate.from_template(template)

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        rag_chain_instance = rag_chain
        print("Local AI (LlamaCpp) đã sẵn sàng!")
        return rag_chain_instance

    except Exception as e:
        print(f"LỖI KHỞI TẠO LOCAL AI: {e}")
        return None

# --- HÀM 3: GỌI TỪ VIEW ---
def get_chatbot_response(question):
    rag_chain = initialize_rag_chain()
    
    if not rag_chain:
        return "Lỗi: Không thể khởi tạo AI Model. Vui lòng kiểm tra file model trong thư mục."
        
    try:
        # Invoke chain
        response = rag_chain.invoke(question)
        return response
    except Exception as e:
        print(f"Lỗi khi trả lời: {e}")
        return "Xin lỗi, tôi đang gặp sự cố hệ thống."