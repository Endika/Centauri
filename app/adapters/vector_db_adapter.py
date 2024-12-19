import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

import chromadb
from app.config import OPEN_API_KEY

logger = logging.getLogger(__name__)


class VectorDBAdapter:
    def __init__(
        self, db_path: str = "chromadb", collection_name: str = "help_center"
    ):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def load_and_store_documents(
        self, file_path: str, chunk_size: int = 500, chunk_overlap: int = 50
    ):
        with open(file_path, "r", encoding="utf-8") as file:
            document = file.read()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        chunks = [
            chunk for chunk in splitter.split_text(document) if chunk.strip()
        ]

        embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
        vectors = embeddings.embed_documents(chunks)

        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                metadatas={"chunk_id": i},
                ids=[f"doc_{i}"],
                embeddings=[vectors[i]],
            )

    def query(self, question: str, top_k=1) -> str:
        embedding = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
        query_embedding = embedding.embed_query(question)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        return results
