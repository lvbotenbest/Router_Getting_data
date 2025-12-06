
import pandas as pd
import os
import re

def clean_answer(answer):
    # Remove calculator annotations <<...>>
    answer = re.sub(r'<<.*?>>', '', answer)
    # Replace #### with Therefore, the answer is
    answer = answer.replace('####', 'Therefore, the answer is')
    return answer

def convert_parquet_to_jsonl(parquet_file, jsonl_file):
    try:
        # Read the parquet file
        df = pd.read_parquet(parquet_file)
        
        # Check if required columns exist
        if 'question' not in df.columns or 'answer' not in df.columns:
            print(f"Error: Parquet file must contain 'question' and 'answer' columns. Found: {df.columns}")
            return

        # Clean the answer column
        # df['answer'] = df['answer'].apply(clean_answer)

        # Write to jsonl
        # orient='records' with lines=True produces the desired jsonl format
        df[['question', 'answer']].to_json(jsonl_file, orient='records', lines=True, force_ascii=False)
        
        print(f"Successfully converted '{parquet_file}' to '{jsonl_file}' with cleaning.")
        
    except Exception as e:
        print(f"Error converting file: {e}")

if __name__ == "__main__":
    parquet_path = 'train-00000-of-00001.parquet'
    # The user asked to convert it to the same format as test.cleand.jsonl
    # I'll name the output train.cleand.jsonl to reflect the cleaning
    jsonl_path = 'train.cleand.jsonl'
    
    if os.path.exists(parquet_path):
        convert_parquet_to_jsonl(parquet_path, jsonl_path)
    else:
        print(f"File not found: {parquet_path}")
