import os
from django.conf import settings
import re
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
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base" # Thư mục chứa file .txt
FAISS_INDEX_DIR = BASE_DIR / "faiss_index" # Thư mục lưu trữ FAISS index
# Đảm bảo tên file model khớp 100% với file bạn tải về
MODEL_PATH = os.path.join(settings.BASE_DIR, "models", "Phi-4-mini-instruct-Q5_K_M.gguf")

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
def initialize_chains():
    global llm_instance, rag_chain_instance, small_talk_chain_instance
    if rag_chain_instance: # Nếu đã load rồi thì bỏ qua
        return

    print(f"Đang khởi tạo Local AI Model (Phi-3-mini) từ: {MODEL_PATH} ...")
    
    if not os.path.exists(MODEL_PATH):
        print(f"LỖI: Không tìm thấy file model Phi-3 tại {MODEL_PATH}")
        return

    try:
        # 1. Khởi tạo LLM (Bộ não chính) - CHỈ 1 LẦN
        llm = LlamaCpp(
            model_path=str(MODEL_PATH),
            temperature=0.1, max_tokens=512, n_ctx=4096,
            n_threads=8,
            top_p=1, verbose=False, 
            main_gpu=0,
            n_gpu_layers= -1 # Tùy cấu hình máy
        )
        llm_instance = llm

        # 2. Khởi tạo Chain RAG (Dùng để tra cứu nghiệp vụ)
        vector_store = load_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Chỉ lấy 1 đoạn
        
        rag_template = """<|system|>
        You are a virtual receptionist for "The Sailing Bay" resort.
        Your task is to answer the user's question based *ONLY* on the provided "Context".
        Do not invent or make up information. If the Context does not have the answer, you MUST say "Dạ em xin lỗi, em chưa có thông tin này ạ."

        IMPORTANT: You MUST answer *ONLY* in Vietnamese (TIẾNG VIỆT).
        You must address the user as 'quý khách' and yourself as 'em'.
        <|end|>
        <|user|>
        Context:
        {context}

        Question: {question}
        <|end|>
        <|assistant|>
        """
        rag_prompt = ChatPromptTemplate.from_template(rag_template)
        rag_chain_instance = (
            {"context": retriever, "question": RunnablePassthrough()}
            | rag_prompt
            | llm
            | StrOutputParser()
        )

        # 3. Khởi tạo Chain Small Talk (Dùng để chào hỏi)
        small_talk_template = """<|system|>
        You are a friendly virtual receptionist for "The Sailing Bay" resort.
        Your task is to provide a short, friendly greeting (e.g., "Dạ em chào quý khách ạ") and ask how you can help.
        DO NOT talk about history, politics, or any other topic.

        IMPORTANT: You MUST answer *ONLY* in Vietnamese (TIẾNG VIỆT).
        You must address the user as 'quý khách' and yourself as 'em'.
        <|end|>
        <|user|>
        {question}
        <|end|>
        <|assistant|>
        """
        small_talk_prompt = ChatPromptTemplate.from_template(small_talk_template)
        small_talk_chain_instance = small_talk_prompt | llm | StrOutputParser()
        
        print("AI (RAG và Small Talk) đã sẵn sàng!")

    except Exception as e:
        print(f"LỖI KHỞI TẠO LOCAL AI: {e}")

# --- 4. DANH SÁCH TỪ KHÓA CHÀO HỎI (Router) ---
SMALL_TALK_KEYWORDS = [
    'xin chào', 'hello', 'hi', 'chào bạn', 'chào em', 
    'cảm ơn', 'cám ơn', 'thanks', 'thank you', 'ok', 'oke',
    'tạm biệt', 'bye'
]

def is_small_talk(question):
    # Chuẩn hóa câu hỏi: chuyển về chữ thường, xóa dấu câu, ký tự đặc biệt
    question_lower = question.lower().strip()
    question_normalized = re.sub(r'[^\w\s]', '', question_lower)
    
    # Kiểm tra xem câu hỏi CÓ CHỨA từ khóa hay không
    # thay vì CHÍNH XÁC LÀ từ khóa
    for keyword in SMALL_TALK_KEYWORDS:
        if keyword in question_normalized:
            # Thêm điều kiện: nếu câu hỏi quá dài, có thể không phải small talk
            if len(question_normalized.split()) <= 5:
                return True
    return False

# --- 5. HÀM CHÍNH ĐỂ GỌI TỪ VIEW (ĐÃ CÓ ROUTER) ---
def get_chatbot_response(question):
    # 1. Khởi tạo (nếu chưa)
    initialize_chains() 
    
    if not rag_chain_instance or not small_talk_chain_instance:
        return "Lỗi: AI chưa sẵn sàng. Vui lòng kiểm tra log server."

    # 2. BỘ ĐỊNH TUYẾN (ROUTER)
    if is_small_talk(question):
        # Nếu là chào hỏi -> Dùng Chain "Chào hỏi" (KHÔNG TÌM KIẾM)
        print(f"Router: Đang xử lý Small Talk cho: '{question}'")
        try:
            return small_talk_chain_instance.invoke({"question": question})
        except Exception as e:
            print(f"Lỗi Small Talk Chain: {e}")
            return "Dạ em chào quý khách ạ." # Trả lời dự phòng
    else:
        # Nếu là nghiệp vụ -> Dùng Chain "RAG" (CÓ TÌM KIẾM)
        print(f"Router: Đang tra cứu RAG cho: '{question}'")
        try:
            return rag_chain_instance.invoke(question)
        except Exception as e:
            print(f"Lỗi RAG Chain: {e}")
            return "Xin lỗi, em đang gặp sự cố khi tra cứu."