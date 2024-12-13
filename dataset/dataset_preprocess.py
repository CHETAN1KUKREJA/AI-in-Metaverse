from datasets import load_dataset
import json

ds = load_dataset("jingjietan/pandora-big5")

alpaca_json = []

datasets = [ds["train"], ds["validation"], ds["test"]]
for dataset in datasets:
    for sample in dataset:
        instruction = f"You are a helpful assistant with the following Big Five personality traits: Openness - {sample['O']}, Conscientiousness - {sample['C']}, Extraversion - {sample['E']}, Agreeableness - {sample['A']}, Neuroticism - {sample['N']}"
        input = ""
        output = sample["text"]
        
        alpaca_json.append({"instruction": instruction, "input": input, "output": output})
        
with open('result.json', 'w') as fp:
    json.dump(alpaca_json, fp, indent=4)
