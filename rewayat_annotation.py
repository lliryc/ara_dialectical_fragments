# vllm_openai_client_example.py
import os
import json
import random
from typing import List, Dict, Any
from collections import defaultdict
import tqdm
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

# OpenAI SDK v1.x
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

os.environ["VLLM_MODEL_NAME"] = "openai/gpt-oss-120b"
load_dotenv()

# --- Config ---
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://10.127.7.212:8000/v1")
API_KEY  = os.getenv("OPENAI_API_KEY", "EMPTY")  # vLLM doesn't check this
MODEL    = os.getenv("VLLM_MODEL_NAME", "openai/gpt-oss-120b")

llm = ChatOpenAI(
    model=MODEL,
    openai_api_key=API_KEY,
    openai_api_base=BASE_URL,
    max_tokens=120000,
    temperature=0.6,
)

# Create JSON output parser
json_parser = JsonOutputParser()

llm_json= llm | json_parser

def dialogues_semantic_split(
    dialogues_str: str
) -> str:
    messages = [
      SystemMessage(
        content="You are a helpful assistant and Gulf dialect native speaker."
      ),
      HumanMessage(
        content=f"""Split the dialogues in Gulf Arabic dialect into sequential groups of lines that are related to the same topic.
        Dialogues are represented as jsonl with one line per line (line id corresponds to the line id).
        Output the sequential groups of lines as JSON array with the following structure:
        
        [
            {{
                "split_id": "sequential number",
                "topic": "precise description of topic written in Modern Standard Arabic (in no more than 5 words)",
                "line_ids": "sequence of line ids separated by commas"
            }}
        ]
        
        Each group should contain lines that discuss the same topic or theme. Be precise and concise in your topic descriptions.
        IMPORTANT: Do not include any other text in your response. Otherwise you will be fined 1000$ for each violation.
        
        
        Dialogues in Gulf Arabic dialect:
        ---------------------------------------------
        {dialogues_str}
        ---------------------------------------------
"""
      )
    ]
    res = llm_json.invoke(messages)
    return res

def process_file(filepath: str) -> None:
    """Process a single file with speech_transcription_semantic_split"""
    filename = os.path.basename(filepath)
    
    
    output_file_path = os.path.join("output_data/gpt-oss-120b", filename + '.jsonl')
    
    if os.path.exists(output_file_path):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        dialogues_str = f.read()
        
    file_id = filename
    
    try:
        answer = dialogues_semantic_split(dialogues_str)
        print(f"\n[speech_transcription_semantic_split for {filename}]\n", answer)
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            for split in answer:
                split['file_id'] = file_id
                split_str = json.dumps(split, ensure_ascii=False)
                f_out.write(split_str + '\n')
    except Exception as e:
        print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    print(f"Using base_url={BASE_URL}, model={MODEL}")
    os.makedirs("output_data/gpt-oss-120b", exist_ok=True)
    
    files = glob.glob("data_rewayat_jsonl/*.jsonl")
    
    files = list(files)
    
    random.shuffle(files)
    
    files = files[:4000] # random sample of 4000 files
    
    files = list(sorted(files)) 
    
    # Process files in parallel with 4 workers
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_file, filepath): filepath for filepath in files}
        
        # Process completed tasks with progress bar
        for future in tqdm.tqdm(as_completed(future_to_file), total=len(files)):
            filepath = future_to_file[future]
            try:
                future.result()  # This will raise any exception that occurred
            except Exception as e:
                filename = os.path.basename(filepath)
                print(f"Error processing {filename}: {e}")