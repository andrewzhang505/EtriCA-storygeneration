import os
import json
import subprocess
import openai
import re
import sys
sys.path.append("../../../utils")
from limerick_metrics import LimerickEvaluator

def generate_gpt3_response(prompt, model="curie:ft-personal-2023-04-18-00-15-52", n=1):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        n=n,
        max_tokens=250,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].text.strip("&")

def main():
    os.environ['OPENAI_API_KEY'] = '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'
    with open("../../../../preprocessed/limerick_dataset_oedilf_v3.json", "r") as f:
        text = json.load(f)

    subprocess.call(['pip', 'install', 'aiohttp'])
    subprocess.call(['pip', 'install', '--upgrade', 'openai'])

    num_trains = int(len(text) * 0.8)
    num_valids = len(text) - num_trains
    new_train_text = []
    new_valid_text = []
    for i in range(num_trains):
        dictionary = {}
        lines = text[i]['limerick'].split("\n")
        dictionary['prompt'] = lines[0]
        newStr = ""
        for j in range(1,len(lines)-1):
            newStr = newStr + lines[j] + "\n"
        newStr = newStr + lines[len(lines)-1]
        dictionary['completion'] = newStr
        new_train_text.append(dictionary)

    for i in range(num_valids):
        dictionary = {}
        lines = text[i+num_trains]['limerick'].split("\n")
        dictionary['prompt'] = lines[0]
        newStr = ""
        for j in range(1,len(lines)-1):
            newStr = newStr + lines[j] + "\n"
        newStr = newStr + lines[len(lines)-1]
        dictionary['completion'] = newStr
        new_valid_text.append(dictionary)

    with open("../../../../preprocessed/limerick_new_data2_train.json", "r") as f:
        json.dump(new_train_text, f)
    with open('../../../../preprocessed/limerick_new_data2_valid.json', 'w') as f:
        json.dump(new_valid_text, f)

    subprocess.call(['openai', 'tools', 'fine_tunes.prepare_data', '-f', 'limerick_new_data2_train.json'])
    subprocess.call(['openai', 'tools', 'fine_tunes.prepare_data', '-f', 'limerick_new_data2_valid.json'])
    subprocess.call(['openai', 'api', 'fine_tunes.create', '-t', 'limerick_new_data2_train_prepared.jsonl', '-m', 'curie'])

    openai.api_key = os.getenv("OPENAI_API_KEY")

    final_output_prompt = []
    for i in range(500):
        final_output_prompt.append(new_valid_text[i]['prompt'])
    final_output_completion = []
    for i in range(500):
        completion = generate_gpt3_response(new_valid_text[i]['prompt']).strip("&")
        final_output_completion.append(completion)
    
    final_output_completion = [re.sub(r"[^\w\s-]|_", "", x.replace("&", "")).replace(" - ", "\n").strip() for x in final_output_completion]
    final_output_completion

    with open("../../../../preprocessed/final_output.json", "w") as f:
        json.dump(final_output_completion, f)

    '''
    with open("../../../preprocessed/final_output.json", "r") as f:
        final_output = json.load(f)
    '''
    lim_eval = LimerickEvaluator(line_sep = "\n")
    metrics = {}

    lim_eval.etrica(final_output_prompt, final_output_completion, metrics)

    

