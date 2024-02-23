# from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from InstructorEmbedding import INSTRUCTOR 
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA


DB_FAISS_PATH = '../vectorstore/db_faiss'

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
    n_gpu_layers = -1
    n_batch = 512

    # Download the .gguf model that you want to implement and then used it
    # It only works for gguf
    llm = LlamaCpp(model_path="../models/ggml-model-q4_0.gguf",
      n_gpu_layers=n_gpu_layers,
      n_batch=n_batch,
      max_tokens=150,
      top_p=1,
      repeat_penalty=1.2,
      top_k=50,
      n_ctx=2048, # Uncomment to increase the context window
      temperature = 0.75,
      verbose=True,
    )
    return llm

def qa_bot():   
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large",
                                        model_kwargs={'device': 'cuda'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    return qa

def main():
    qa = qa_bot()
    query = "What sensors does the humanoid robot ARTEMIS have?"
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


 