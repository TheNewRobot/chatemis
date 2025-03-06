# pip install langchain
from langchain_community.document_loaders import DirectoryLoader # pip install "unstructured[local-inference]" This install torch
import torch
from langchain_text_splitters import CharacterTextSplitter
from InstructorEmbedding import INSTRUCTOR # pip install InstructorEmbedding #pip install sentence-transformers==2.4.0 (we should use this specific version)
from sentence_transformers import SentenceTransformer
import pickle
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS # pip install faiss_gpu
import yaml
from datasets import load_dataset

#import nltk
#nltk.download('punkt_tab')
#nltk.download('averaged_perceptron_tagger_eng')

class Tokenizer:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.data_path = config['tokenizer']['data_path']
        self.index_path = config['tokenizer']['db_faiss_path']
        self.separator = config['tokenizer']['text_spliter']['separator']
        self.chunk_size = config['tokenizer']['text_spliter']['chunk_size']
        self.chunk_overlap = config['tokenizer']['text_spliter']['chunk_overlap']
        self.is_separator = config['tokenizer']['text_spliter']['is_separator']
        self.model_name = config['tokenizer']['instructor_embeddings']
        self.device = []

    def check_cuda(self):
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print("You are good to go with cuda! Device: ", device_name)
            self.device = 'cuda'
        else:
            print("You are good to go with cpu!")
            self.device = 'cpu'

    def load_data(self):
        loader = DirectoryLoader(self.data_path, glob="**/*.pdf", show_progress=True, use_multithreading=True)
        docs = loader.load()
        return docs

    def split_into_chunks(self,docs):
        text_splitter = CharacterTextSplitter(
            separator= self.separator,
            chunk_size= self.chunk_size,
            chunk_overlap= self.chunk_overlap,
            length_function=len,
            is_separator_regex= self.is_separator ,
        )
        texts = text_splitter.split_documents(docs)
        return texts

    def store_embeddings(self,texts,device):
        # Embedddings
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        instructor_embeddings = HuggingFaceInstructEmbeddings(model_name=self.model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
        db = FAISS.from_documents(texts, instructor_embeddings)
        db.save_local(self.index_path)

if __name__ == "__main__":
    tokenizer = Tokenizer("./config.yaml")
    tokenizer.check_cuda()
    docs = tokenizer.load_data()
    texts = tokenizer.split_into_chunks(docs)
    tokenizer.store_embeddings(texts,tokenizer.device)
    print("Documents loaded!")
