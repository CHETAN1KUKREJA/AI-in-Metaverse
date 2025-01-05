# Environment Setup

```bash
# create conda environment
conda create -n aimetaverse python=3.10 -y
conda activate aimetaverse

# install packages
pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --index-url https://download.pytorch.org/whl/cu118
pip install transformers
pip install modelscope
pip install transformers
pip install streamlit
pip install sentencepiece
pip install accelerate
pip install datasets
pip install peft
pip install huggingface_hub
pip install regrex
```

For a faster attention calculation, FlashAttention is used, but it needs to use the cuda compiler to build:

```bash
# make sure the gcc version is 11
# install cuda however you want, use the version 11.8
MAX_JOBS=8 pip install flash-attn --no-build-isolation
```

Install auto-awq for AWQ Quantization:

```bash
INSTALL_KERNELS=1 pip install git+https://github.com/casper-hansen/AutoAWQ.git
```

Install langchain:

```bash
pip install langchain
pip install accelerate
pip install -U bitsandbytes
```