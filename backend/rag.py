import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()

FAISS_PATH = "faiss_index"
API_KEY = os.environ.get("OPENAI_API_KEY")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://openrouter.ai/api/v1")

print(f"🔑 Key: {API_KEY[:15] if API_KEY else 'NOT FOUND'}")
print(f"🌐 Base: {API_BASE}")

# Free local embeddings — no API needed, runs on your machine
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )


def build_knowledge_base():
    print("📚 Loading knowledge files...")
    loader = DirectoryLoader("knowledge/", glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"   Loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"   Split into {len(chunks)} chunks")

    print("🔢 Creating embeddings (free, local model)...")
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_PATH)
    print("✅ Knowledge base saved!")
    return vector_store


def load_knowledge_base():
    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store


def create_chain(vector_store):
    # OpenRouter handles the chat/LLM part just fine
    llm = ChatOpenAI(
        model_name="openai/gpt-4o-mini",
        temperature=0.3,
        openai_api_key=API_KEY,
        openai_api_base=API_BASE,
        default_headers={
            "HTTP-Referer": "https://agronexustrading.in",
            "X-Title": "Agronexus Chatbot"
        }
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    return chain


SYSTEM_PROMPT = """You are AgroBot, the friendly customer assistant for
Agronexus Trading Co., a premium Indian spice and mango export company
based in Toronto, Canada. Answer questions about products, pricing,
shipping, and orders. If unsure, direct to info@agronexustrading.in.
Keep answers concise and professional."""


def ask(chain, question, chat_history=[]):
    full_question = f"{SYSTEM_PROMPT}\n\nCustomer question: {question}"
    response = chain.invoke({
        "question": full_question,
        "chat_history": chat_history
    })
    return response["answer"]


if __name__ == "__main__":
    build_knowledge_base()
    print("\n🧪 Testing...")
    vs = load_knowledge_base()
    chain = create_chain(vs)
    answer = ask(chain, "What spices do you sell?")
    print(f"\nBot: {answer}")
