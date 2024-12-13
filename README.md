# LLM-Backend

## Personality

### Fine-tuning

#### Setup

Setup python environment using `environment_setup.md`.

Login into hugging face:

```bash
pip install --upgrade huggingface_hub
huggingface-cli login
```

Clone the LLaMA-Factory:

```bash
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"
```

Note that the folder may conflict. Rename the existing LLaMA-Factory folder before cloning. Move the folder inside the original one back into the cloned LLaMA-Factory. The relative path should not change. You might need to remove the `.git` folder inside LLaMA-Factory.

#### Dataset

I used the PANDORA big 5 personality dataset for fine-tuning the llama-3.1-8B-Instruct model. Here is a sample input:

```
{
    "instruction": "You are a helpful assistant with the following Big Five personality traits: Openness - 13.0, Conscientiousness - 94.0, Extraversion - 83.0, Agreeableness - 47.0, Neuroticism - 90.0",
    "input": "",
    "output": "I constantly think about this. Being diagnosed a couple months ago and being engaged to a wonderful woman who is perfect in every way has become a bit difficult.  We both have wanted big families since we were little. She was adopted from South Korea and has no knowledge  of her parents from there. It's honestly going to be a gamble for us. I recently just found out mental illness does run in my family so god knows what else does."
    }
```

### Prompt