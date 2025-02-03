# llm.py
from fastapi import Depends
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import List, TypedDict
from .config import get_llm_config, LLMConfig

TEXT_FILE_PATH = "./text/hume_treatise.txt"

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

def build_graph(vector_store: Chroma, llm) -> CompiledStateGraph:
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

def get_vector_store(llm_config: LLMConfig = Depends(get_llm_config)) -> Chroma:
    """
    Get or create the vector store as a dependency.
    """
    embeddings = llm_config.get_embeddings()
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory="vector_store"
    )
    
    # Only load documents if the collection is empty
    if not vector_store._collection.count():
        split_docs = load_split_text(TEXT_FILE_PATH)
        vector_store.add_documents(documents=split_docs)
        
    return vector_store

def get_rag_graph(
    vector_store: Chroma = Depends(get_vector_store),
    llm_config: LLMConfig = Depends(get_llm_config)
) -> CompiledStateGraph:
    """
    Get the RAG graph as a FastAPI dependency.
    """
    return build_graph(vector_store, llm_config.get_llm())