# pip install langchain
from langchain_community.document_loaders import DirectoryLoader # pip install "unstructured[local-inference]" This install torch 
import torch
from langchain.text_splitter import CharacterTextSplitter
from InstructorEmbedding import INSTRUCTOR # pip install InstructorEmbedding #pip install sentence-transformers==2.2.2 (we should use this specific version)
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
import pickle
from langchain_community.vectorstores import FAISS # pip install faiss_gpu 
import yaml

with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

DATA_PATH = config['saving_tokens']['data_path']
DB_FAISS_PATH = config['saving_tokens']['db_faiss_path']


def check_cuda():
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)  
        print("You are good to go with cuda! Device: ", device_name)
        device = 'cuda'
    else:
        print("You are good to go with cpu!")
        device = 'cpu'
    return device 

def load_data():
    loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", show_progress=True, use_multithreading=True)
    docs = loader.load()
    return docs

def split_into_chunks(docs):
    text_splitter = CharacterTextSplitter(
        separator= config['saving_tokens']['text_spliter']['separator'],
        chunk_size= config['saving_tokens']['text_spliter']['chunk_size'],
        chunk_overlap= config['saving_tokens']['text_spliter']['chunk_overlap'],
        length_function=len,
        is_separator_regex= config['saving_tokens']['text_spliter']['is_separator'],
    )
    texts = text_splitter.split_documents(docs)
    return texts

def store_embeddings(texts,device):
    # Embedddings
    # Run this once so it downloads the embedding model,
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name=config['saving_tokens']['instructor_embeddings'],
                                                        model_kwargs={"device":device})

    # This will generate 
    db = FAISS.from_documents(texts, instructor_embeddings)
    db.save_local(DB_FAISS_PATH)

def main():
    device = check_cuda()
    docs = load_data()
    texts = split_into_chunks(docs)
    store_embeddings(texts,device)
    print("Documents loaded!")

if __name__=='__main__':
    main()