import os
from openai import OpenAI
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.embeddings import Embeddings
from typing import List

load_dotenv()

FAISS_PATH = "faiss_index"
CHAT_KEY  = os.environ.get("OPENAI_API_KEY")
CHAT_BASE = os.environ.get("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
EMBED_KEY = os.environ.get("OPENAI_EMBEDDING_KEY")

print(f"🔑 Chat key:  {CHAT_KEY[:15] if CHAT_KEY else 'NOT FOUND'}")
print(f"🔑 Embed key: {EMBED_KEY[:15] if EMBED_KEY else 'NOT FOUND'}")
print(f"🌐 Chat base: {CHAT_BASE}")


class DirectOpenAIEmbeddings(Embeddings):
    """
    Calls OpenAI embeddings API directly using the openai client.
    Bypasses LangChain's OpenAIEmbeddings which ignores api_key parameter.
    """
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=[text],
            model=self.model
        )
        return response.data[0].embedding


def get_embeddings():
    return DirectOpenAIEmbeddings(api_key=EMBED_KEY)


def build_knowledge_base():
    print("📚 Loading knowledge files...")
    loader = DirectoryLoader("knowledge/", glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"   Loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"   Split into {len(chunks)} chunks")

    print("🔢 Creating embeddings via OpenAI...")
    vector_store = FAISS.from_documents(chunks, get_embeddings())
    vector_store.save_local(FAISS_PATH)
    print("✅ Knowledge base saved!")
    return vector_store


def load_knowledge_base():
    return FAISS.load_local(
        FAISS_PATH,
        get_embeddings(),
        allow_dangerous_deserialization=True
    )


def create_chain(vector_store):
    llm = ChatOpenAI(
        model_name="openai/gpt-4o-mini",
        temperature=0.3,
        openai_api_key=CHAT_KEY,
        openai_api_base=CHAT_BASE,
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
based in Toronto, Canada with sourcing operations in Gujarat.
Answer questions about products, pricing, shipping, and policies.
Be warm, professional, and concise (2-4 sentences).
If unsure, direct to info@agronexustrading.in.
Never make up prices or specs."""


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
