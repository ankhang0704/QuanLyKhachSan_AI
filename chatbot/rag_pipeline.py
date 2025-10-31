import os
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
# Sửa lỗi 1 (lỗi đọc file .txt):
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# === SỬA LỖI IMPORT (LỖI 2) ===
# Xóa import cũ: from langchain_community.embeddings import HuggingFaceEmbeddings
# Thêm import mới:
from langchain_huggingface import HuggingFaceEmbeddings
# === KẾT THÚC IMPORT ===


# 1. Cấu hình API Key (Lấy từ Google AI Studio)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAMAuRPaz4gjWiBoaViItzj8Y7gkdGiBqw" 

# 2. Định nghĩa các đường dẫn
BASE_DIR = settings.BASE_DIR
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
FAISS_INDEX_DIR = BASE_DIR / "faiss_index"

# 3. Hàm tạo mới hoặc tải Vector Store
def load_vector_store():
    # === SỬA LỖI CRASH (LỖI 1) ===
    # Dùng đúng tên model và đúng tham số "model_name"
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists(FAISS_INDEX_DIR):
        print("Đang tải Vector Store từ file...")
        vector_store = FAISS.load_local(
            FAISS_INDEX_DIR, 
            embeddings, 
            allow_dangerous_deserialization=True 
        )
    else:
        print("Chưa có Vector Store. Đang tạo mới...")
        # Sửa lỗi đọc file .txt (từ lần trước)
        loader = DirectoryLoader(
            KNOWLEDGE_BASE_DIR, 
            glob="*.txt", 
            loader_cls=TextLoader, 
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        vector_store = FAISS.from_documents(texts, embeddings)
        
        vector_store.save_local(FAISS_INDEX_DIR)
        print(f"Đã tạo và lưu Vector Store tại {FAISS_INDEX_DIR}")
        
    return vector_store

# 4. Tải LLM (Gemini) và tạo "Chain" mới
try:
    llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0.7)
    vector_store = load_vector_store() # Gọi hàm
    
    retriever = vector_store.as_retriever() # Biến vector_store thành "Bộ tìm kiếm"

    template = """Bạn là một trợ lý AI hữu ích cho khách sạn The Sailing Bay.
    Hãy sử dụng các thông tin được cung cấp sau đây để trả lời câu hỏi của người dùng.
    Nếu thông tin không có trong nội dung được cung cấp, hãy nói rằng bạn không biết câu trả lời.
    Hãy trả lời một cách thân thiện và chuyên nghiệp.

    Thông tin:
    {context}

    Câu hỏi:
    {question}

    Câu trả lời:"""
    prompt = ChatPromptTemplate.from_template(template)

    # Chain (dùng |)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

except Exception as e:
    print(f"Lỗi khi tải mô hình Gemini hoặc tạo Chain: {e}")
    rag_chain = None

# 5. Hàm chính để gọi từ Django
def get_chatbot_response(question):
    if not rag_chain:
        return "Lỗi: Chatbot chưa được khởi tạo đúng cách. Vui lòng kiểm tra API Key hoặc log khởi động."
        
    try:
        response_string = rag_chain.invoke(question)
        return response_string
    except Exception as e:
        print(f"Lỗi RAG: {e}")
        return "Xin lỗi, tôi đang gặp sự cố. Vui lòng thử lại sau."