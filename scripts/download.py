import sys
from huggingface_hub import snapshot_download

if len(sys.argv) != 2:
    print("Usage: python download.py <model_id>")
    sys.exit(1)

token_hugging_face = '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'
model_id = sys.argv[1]
local_dir = model_id.replace("/", "-")
snapshot_download(repo_id=model_id, local_dir=local_dir, token=token_hugging_face,
                  local_dir_use_symlinks=False, revision="main")