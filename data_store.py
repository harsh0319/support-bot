from settings import *
import uuid
from qdrant_client.http.models import PointStruct
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient, models
from langchain.text_splitter import CharacterTextSplitter
from openai import OpenAI

openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)


client = QdrantClient(
    url=QDRANT_URL, 
    api_key=QDRANT_KEY,
    timeout=60
)


class store_data_vectors:

    def __init__(self):
        pass

    def create_collection(self):
        client.recreate_collection(
            collection_name="customer_complaints_collection",
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
        )

    def create_data_chunks(self,text:str):

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
        )

        chunks=text_splitter.split_text(text)

        return chunks
    
    def create_embeddings(self,text_chunk):

        points = []
        for id, chunk in enumerate(text_chunk):

            
            response = openai_client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
            vectors = response.data[0].embedding
            point_id = str(uuid.uuid4())

            points.append(PointStruct(id=point_id,vector=vectors,payload={"text":chunk}))
        print("embeddings created")
        return points
    

    def extract_text_from_pdf(self,file_path):

        text = ""

        with open(file_path,'rb') as data:

            Pdf_reader = PdfReader(data)

            for page in Pdf_reader.pages:
                text+=page.extract_text()
        

        return text
    


    def insert_data(self, points):

        client.upsert(
            collection_name="customer_complaints_collection",
            points = points
        )

    
    def main(self,file_path):


        self.create_collection()
        get_data= self.extract_text_from_pdf(file_path)
        chunks = self.create_data_chunks(get_data)
        embedding = self.create_embeddings(chunks)
        self.insert_data(embedding)
    
obj_store_data_vectors = store_data_vectors()

obj_store_data_vectors.main("customer-complaints-management-policy-procedure.pdf")

    