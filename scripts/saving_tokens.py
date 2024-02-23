# pip install langchain
from langchain_community.document_loaders import DirectoryLoader # pip install "unstructured[local-inference]" This install torch 
import torch
from langchain.text_splitter import CharacterTextSplitter
from InstructorEmbedding import INSTRUCTOR # pip install InstructorEmbedding #pip install sentence-transformers==2.2.2 (we should use this specific version)
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
import pickle
from langchain_community.vectorstores import FAISS # pip install faiss_gpu 

# TODO: Define the cached folder

DATA_PATH = '../data/'
DB_FAISS_PATH = '../vectorstore/db_faiss'

if torch.cuda.is_available():
    device_name = torch.cuda.get_device_name(0)  
    print("You are good to go with cuda! Device: ", device_name)
    device = 'cuda'
else:
    print("You are good to go with cpu!")
    device = 'cpu'

loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", show_progress=True, use_multithreading=True)
docs = loader.load()
# Splitter
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)
texts = text_splitter.split_documents(docs)

# Embedddings

# Run this once so it downloads the embedding model,
instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large",
                                                    model_kwargs={"device":device})
# instructor_embeddings = HuggingFaceInstructEmbeddings(cached_folder="~/.cache/torch/sentence_transformers/hkunlp_instructor-large/pytorch_model.bin",
#                                                     model_kwargs={"device":device})
# This will generate 
db = FAISS.from_documents(texts, instructor_embeddings)
db.save_local(DB_FAISS_PATH)

###################################################################################


print("Documents loaded!")