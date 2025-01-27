from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import List, TypedDict

TEXT_FILE_PATH = "./text/theodorus.txt"

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def load_split_text(text_file_path: str) -> List[Document]:
    """
    Load and split text documents into overlapping chunks.
    """
    loader = TextLoader(text_file_path, encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    split_docs = text_splitter.split_documents(docs)

    return split_docs




def build_graph(vector_store: Chroma, llm: ChatOllama) -> CompiledStateGraph:
    """
    Build a state graph for the RAG system.
    """
    prompt = hub.pull("rlm/rag-prompt")

    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"], k=3)
        return {"context": retrieved_docs}

    def generate(state: State):
        docs_content = "\n\n".join(
            doc.page_content for doc in state["context"])
        messages = prompt.invoke(
            {"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}

    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    return graph

def setup_llm() -> CompiledStateGraph:
    """
    Setup the LLM, word embeddings and vector store. 
    Load documents into the vector store. Build the state graph.
    """
    # from langchain_openai import ChatOpenAI
    # from langchain_openai import OpenAIEmbeddings
    # llm = ChatOpenAI(model="gpt-4o-mini")
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    llm = ChatOllama(
        model="deepseek-r1:1.5b",
        temperature=0.0,
    )
    embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
    vector_store = Chroma(embedding_function=embeddings,
                          persist_directory="vector_store")
    
    split_docs = load_split_text(TEXT_FILE_PATH)
    vector_store.add_documents(documents=split_docs)
    graph = build_graph(vector_store, llm)

    return graph

