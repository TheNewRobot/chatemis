from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader # pip install "unstructured[local-inference]" This install torch 

from langchain.text_splitter import CharacterTextSplitter
import torch
import yaml
import glob

class Tokenizer:
	def __init__(self, config_path):
		with open(config_path, "r") as f:
			config = yaml.safe_load(f)
		self.data_path = config['tokenizer']['data_path']
		self.embedding_model_name = config['tokenizer']['instructor_embeddings']
		self.index_path = config['tokenizer']['db_faiss_path']
		
		if torch.cuda.is_available():
			device_name = torch.cuda.get_device_name(0)  
			print("You are good to go with cuda! Device: ", device_name)
			self.device = 'cuda'
		else:
			print("You are good to go with cpu!")
			self.device = 'cpu'
		
	def setup(self):
		model_kwargs = {"device": self.device}

		embeddings = HuggingFaceEmbeddings(
		    model_name=self.embedding_model_name,
		    model_kwargs=model_kwargs
		)

		print("embeddings loaded")
		loader = DirectoryLoader(self.data_path, glob="**/*.pdf", show_progress=True, use_multithreading=True)
		documents = loader.load()
		print("docs loaded")
		# Split the document into chunks
		text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
		docs = text_splitter.split_documents(documents=documents)
		print("docs split")
		# Create FAISS vector store
		vectorstore = FAISS.from_documents(docs, embeddings)
		print("vectors extracted")
		# Save and reload the vector store

		vectorstore.save_local(self.index_path)
		print("vectors saved")
		persisted_vectorstore = FAISS.load_local(self.index_path, embeddings, allow_dangerous_deserialization=True)

		# Create a retriever
		return persisted_vectorstore.as_retriever()

tok = Tokenizer("./config.yaml")
tok.setup()
