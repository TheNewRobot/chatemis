from torch import cuda, bfloat16
import transformers
import torch
from langchain_community.llms import HuggingFacePipeline
from langchain_community.llms import CTransformers

model_id = 'meta-llama/Llama-2-7b-chat-hf'
config = transformers.AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.init_device = "cuda"

model = transformers.AutoModelForCausalLM.from_pretrained(
 model_id, config=config, torch_dtype=torch.bfloat16, trust_remote_code=True,
 use_auth_token=hf_auth,
).to("cuda:0")
model.eval()

tokenizer = transformers.AutoTokenizer.from_pretrained(
 model_id,
 use_auth_token=hf_auth
)

generate_text = transformers.pipeline(
 model=model,
 tokenizer=tokenizer,
 return_full_text=True,  # langchain expects the full text
 task='text-generation',
 temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
 max_new_tokens=256,  # max number of tokens to generate in the output
 repetition_penalty=1.1,  # without this output begins repeating
 torch_dtype=torch.float16,
 device='cuda:0'
)

llm = HuggingFacePipeline(pipeline=generate_text)