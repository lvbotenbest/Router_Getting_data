# -*- coding: utf-8 -*-
"""
Script to match prompts between input_data.jsonl and model output files,
create temporary matched files, and run IFEval evaluation.

This script:
1. Reads the input data from input_data.jsonl
2. Reads each model's output from BaseModel_Output/IFEVAL folder
3. Matches prompts between input and output
4. Creates temporary files for each model in BaseModel_Test/IFEval/[model_name]
5. The temporary files can be used for evaluation

Usage:
    python match_and_eval.py
"""

import json
import os
import re
from pathlib import Path


def get_model_name_from_filename(filename):
    """
    Extract model name from the output filename.
    Example: result_Qwen_Qwen3-235B-A22B-Instruct-2507_IFEVAL.jsonl
             -> Qwen_Qwen3-235B-A22B-Instruct-2507
    """
    # Remove prefix 'result_' and suffix '_IFEVAL.jsonl'
    match = re.match(r'result_(.+)_IFEVAL\.jsonl', filename)
    if match:
        return match.group(1)
    return filename.replace('.jsonl', '')


def read_input_data(input_file_path):
    """
    Read input data from input_data.jsonl
    Returns a dictionary mapping prompt to full input data
    """
    inputs = {}
    with open(input_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                inputs[data['prompt']] = data
    return inputs


def read_model_output(output_file_path):
    """
    Read model output from a JSONL file.
    Returns a list of output records.
    """
    outputs = []
    with open(output_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                outputs.append(data)
    return outputs


def match_and_create_temp_files(input_data, model_outputs, model_name, output_dir):
    """
    Match prompts between input data and model outputs.
    Create two temporary files:
    1. matched_input_data.jsonl - matched input data
    2. matched_response_data.jsonl - matched response data
    
    Note: Only keeps the first occurrence of each prompt (no duplicates).
    
    Returns the count of matched items.
    """
    # Create output directory for this model
    model_output_dir = Path(output_dir) / model_name
    model_output_dir.mkdir(parents=True, exist_ok=True)
    
    matched_input = []
    matched_response = []
    matched_prompts = set()  # Track already matched prompts to avoid duplicates
    matched_count = 0
    unmatched_count = 0
    duplicate_count = 0
    
    for output in model_outputs:
        # The model output uses 'original_prompt' as the key
        prompt = output.get('original_prompt', '')
        
        # Skip if already matched (duplicate)
        if prompt in matched_prompts:
            duplicate_count += 1
            continue
        
        if prompt in input_data:
            # Found a match
            input_record = input_data[prompt]
            
            # Create input record (same format as input_data.jsonl)
            matched_input.append(input_record)
            
            # Create response record (format expected by evaluation_lib)
            response_record = {
                'prompt': prompt,
                'response': output.get('response')
            }
            matched_response.append(response_record)
            matched_prompts.add(prompt)  # Mark as matched
            matched_count += 1
        else:
            unmatched_count += 1
    
    # Write matched input data
    input_file = model_output_dir / 'matched_input_data.jsonl'
    with open(input_file, 'w', encoding='utf-8') as f:
        for record in matched_input:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Write matched response data
    response_file = model_output_dir / 'matched_response_data.jsonl'
    with open(response_file, 'w', encoding='utf-8') as f:
        for record in matched_response:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"Model: {model_name}")
    print(f"  Matched: {matched_count}, Duplicates skipped: {duplicate_count}, Unmatched: {unmatched_count}")
    print(f"  Created: {input_file}")
    print(f"  Created: {response_file}")
    
    return matched_count


def main():
    # Define paths
    base_dir = Path(__file__).parent.parent
    
    # Input data path
    input_data_path = base_dir / 'BaseModel_Test' / 'instruction_following_eval' / 'data' / 'input_data.jsonl'
    
    # Model output directory
    model_output_dir = base_dir / 'BaseModel_Output' / 'IFEVAL'
    
    # Output directory for temporary files
    temp_output_dir = base_dir / 'BaseModel_Test' / 'IFEval'
    
    print(f"Input data path: {input_data_path}")
    print(f"Model output directory: {model_output_dir}")
    print(f"Temporary files output directory: {temp_output_dir}")
    print("-" * 60)
    
    # Read input data
    print("Reading input data...")
    input_data = read_input_data(input_data_path)
    print(f"Total input prompts: {len(input_data)}")
    print("-" * 60)
    
    # Process each model output file
    model_files = list(model_output_dir.glob('result_*_IFEVAL.jsonl'))
    print(f"Found {len(model_files)} model output files")
    print("-" * 60)
    
    for model_file in sorted(model_files):
        model_name = get_model_name_from_filename(model_file.name)
        print(f"\nProcessing: {model_file.name}")
        
        # Read model outputs
        model_outputs = read_model_output(model_file)
        print(f"  Total model outputs: {len(model_outputs)}")
        
        # Match and create temp files
        match_and_create_temp_files(input_data, model_outputs, model_name, temp_output_dir)
    
    print("\n" + "=" * 60)
    print("Done! Temporary files created for each model.")
    print("\nTo run evaluation, use the following command for each model:")
    print("  python -m instruction_following_eval.evaluation_main \\")
    print("    --input_data=./IFEval/[model_name]/matched_input_data.jsonl \\")
    print("    --input_response_data=./IFEval/[model_name]/matched_response_data.jsonl \\")
    print("    --output_dir=./IFEval/[model_name]/")


if __name__ == '__main__':
    main()
