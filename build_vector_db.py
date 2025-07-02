from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader

# 讀取 PDF（路徑視情況調整）
loader = PyPDFLoader("data/table_tennis_guide.pdf")
documents = loader.load_and_split()

# 建立向量資料庫
embedding = OpenAIEmbeddings()
db = FAISS.from_documents(documents, embedding)

# 儲存向量資料庫
db.save_local("vectorstore/table_tennis_knowledge")

print("✅ 向量資料庫建立完成")
