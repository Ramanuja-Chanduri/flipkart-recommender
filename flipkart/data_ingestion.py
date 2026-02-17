from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.documents import Document

from flipkart.data_converter import DataConverter
from flipkart.config import config

class DataIngestor:
    def __init__(self):
        self.embedding = HuggingFaceEndpointEmbeddings(model=config.EMBEDDING_MODEL)
        self.vector_store = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="flipkart_database",
            api_endpoint=config.ASTRA_DB_API_ENDPOINT,
            token=config.ASTRA_DB_APPLICATION_TOKEN,
            namespace=config.ASTRA_DB_KEYSPACE
        )
    
    def ingest(self, load_existing=True):
        if load_existing:
            return self.vector_store
        
        data_converter = DataConverter(file_path=config.CSV_FILE_PATH)
        documents = data_converter.covert_to_documents()
        self.vector_store.add_documents(documents)

        return self.vector_store