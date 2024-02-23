# from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from InstructorEmbedding import INSTRUCTOR 
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import yaml

with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

DB_FAISS_PATH = config['saving_tokens']['db_faiss_path']

custom_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Context: {context}
Question: {question}
Only return the helpful answer below and nothing else. Ignore the portions of the context that have the word 'Figures'.
Helpful answer: """

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(search_kwargs={'k': 1}),
                                       chain_type_kwargs={'prompt': prompt}
                                       )
    return qa_chain

def load_llm():
    # Download the .gguf model that you want to implement and then used it
    # It only works for gguf
    llm = LlamaCpp(model_path=config['llm_cpp']['model_path'],
      n_gpu_layers=config['llm_cpp']['load_llm']['n_gpu_layers'],
      n_batch=config['llm_cpp']['load_llm']['n_batch'],
      max_tokens=config['llm_cpp']['load_llm']['max_tokens'],
      top_p=config['llm_cpp']['load_llm']['top_p'],
      repeat_penalty=config['llm_cpp']['load_llm']['repeat_penalty'],
      top_k=config['llm_cpp']['load_llm']['top_k'],
      n_ctx=config['llm_cpp']['load_llm']['n_ctx'], # Uncomment to increase the context window
      temperature = config['llm_cpp']['load_llm']['temperature'],
      verbose=config['llm_cpp']['load_llm']['verbose'],
    )
    return llm

def qa_bot():   
    embeddings = HuggingFaceInstructEmbeddings(model_name=config['saving_tokens']['instructor_embeddings'],
                                        model_kwargs={'device': 'cuda'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    return qa

def main():
    qa = qa_bot()
    query = config['llm_cpp']['query']
    print("------------------")
    print(query)   
    print("------------------")
    print("These are the stats of the response: ")  
    response = qa.invoke({'query': query})
    print("------------------")
    print('This is the answer:')   
    print(response['result'])
    print("------------------")

if __name__ == '__main__':
    main()


 