# from huggingface_hub import hf_hub_download
import torch
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from InstructorEmbedding import INSTRUCTOR 
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import yaml

class LLM_object():
    def __init__(self, config_path):
        with open(config_path, "r") as f:
                config = yaml.safe_load(f)
        self.index_path = config['tokenizer']['db_faiss_path']
        self.llm_model = config['llm_cpp']['model_path']
        self.custom_prompt_template = config['llm_cpp']['custom_prompt_template']
        self.n_gpu_layers = config['llm_cpp']['load_llm']['n_gpu_layers']
        self.n_batch = config['llm_cpp']['load_llm']['n_batch']
        self.max_tokens= config['llm_cpp']['load_llm']['max_tokens']
        self.top_p = config['llm_cpp']['load_llm']['top_p']
        self.repeat_penalty = config['llm_cpp']['load_llm']['repeat_penalty']
        self.top_k = config['llm_cpp']['load_llm']['top_k']
        self.n_ctx = config['llm_cpp']['load_llm']['n_ctx']
        self.temperature = config['llm_cpp']['load_llm']['temperature']
        self.verbose = config['llm_cpp']['load_llm']['verbose']
        self.embeddings_context = config['tokenizer']['instructor_embeddings']
        self.query = config['llm_cpp']['query']
        self.device = []

    def check_cuda(self):
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)  
            print("You are good to go with cuda! Device: ", device_name)
            self.device = 'cuda'
        else:
            print("You are good to go with cpu!")
            self.device = 'cpu'

    def set_custom_prompt(self):
        """
        Prompt template for QA retrieval for each vectorstore
        """
        prompt = PromptTemplate(template=self.custom_prompt_template,
                                input_variables=['context', 'question'])
        return prompt

    def retrieval_qa_chain(self,llm, prompt, db):
        qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type='stuff',
                                        retriever=db.as_retriever(search_kwargs={'k': 1}),
                                        chain_type_kwargs={'prompt': prompt}
                                        )
        return qa_chain

    def load_llm(self):
        # Download the .gguf model that you want to implement and then used it
        # It only works for gguf
        llm = LlamaCpp(model_path=self.llm_model,
                     n_gpu_layers=self.n_gpu_layers,
                          n_batch=self.n_batch,
                       max_tokens=self.max_tokens,
                            top_p=self.top_p,
                   repeat_penalty=self.repeat_penalty,
                            top_k=self.top_k,
                            n_ctx=self.n_ctx, 
                      temperature=self.temperature,
                          verbose=self.verbose)
        return llm

    def qa_bot(self):   
        embeddings = HuggingFaceInstructEmbeddings(model_name=self.embeddings_context,
                                            model_kwargs={'device': self.device})
        db = FAISS.load_local(self.index_path, embeddings)
        llm = self.load_llm()
        qa_prompt = self.set_custom_prompt()
        qa = self.retrieval_qa_chain(llm, qa_prompt, db)
        return qa

if __name__ == '__main__':
    # Run this script as an example so you see how this nodes works
    llama2 = LLM_object("../config.yaml")
    llama2.check_cuda()
    qa = llama2.qa_bot()
    print('We are using this model: ')
    print(llama2.llm_model)
    query = llama2.query
    print("------------------")
    print(query)   
    print("------------------")
    print("These are the stats of the response: ")  
    response = qa.invoke({'query': query})
    print("------------------")
    print('This is the answer:')   
    print(response['result'])
    print("------------------")



 