from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

model_name_or_path = "mistralai/Mistral-7B-v0.1"
model_basename = "pytorch_model-00002-of-00002.bin" # the model is in bin format
model_path = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_gpu_layers = 40 
n_batch = 512

llm = LlamaCpp(
 model_path=model_path,
 max_tokens=512,
 temperature = 0.5,
 n_gpu_layers=n_gpu_layers,
 n_batch=n_batch,
 top_p=0.95,
 repeat_penalty=1.2,
 top_k=50,
 callback_manager=callback_manager,
 verbose=True)

 