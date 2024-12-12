# Environment Setup

```bash
# create conda environment
conda create -n aimetaverse python=3.10 -y
conda activate aimetaverse

# install packages
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers
pip install modelscope==1.9.5
pip install "transformers>=4.40.0"
pip install streamlit==1.24.0
pip install sentencepiece==0.1.99
pip install accelerate==0.29.3
pip install datasets==2.19.0
pip install peft==0.10.0
```

For a faster attention calculation, FlashAttention is used, but it needs to use the cuda compiler to build:

```bash
# make sure the gcc version is 11
# install cuda however you want, use the version 11.8
MAX_JOBS=8 pip install flash-attn --no-build-isolation
```
