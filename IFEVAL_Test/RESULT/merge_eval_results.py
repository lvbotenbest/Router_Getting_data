#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge eval_results_strict.jsonl with BaseModel_Output IFEVAL files.

This script merges the `follow_all_instructions` field from eval_results_strict.jsonl
into the BaseModel_Output/IFEVAL files as a new field named `result`.

The matching is done based on the order of records (line by line matching).
"""

import os
import json
from pathlib import Path


def load_jsonl(file_path):
    """Load a JSONL file and return a list of dictionaries."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def save_jsonl(data, file_path):
    """Save a list of dictionaries to a JSONL file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def get_model_name_from_eval_path(eval_dir_path):
    """Extract model name from eval directory path."""
    return os.path.basename(eval_dir_path)


def find_matching_output_file(model_name, output_dir):
    """Find the matching output file for a given model name."""
    # Expected format: result_{model_name}_IFEVAL.jsonl
    expected_filename = f"result_{model_name}_IFEVAL.jsonl"
    output_file = os.path.join(output_dir, expected_filename)
    
    if os.path.exists(output_file):
        return output_file
    return None


def merge_files(eval_file, output_file, result_file):
    """
    Merge eval_results_strict.jsonl with output file.
    
    The matching is done by the order of records (prompt matching).
    Returns: (total, matched, unmatched, true_count)
    """
    # Load both files
    eval_data = load_jsonl(eval_file)
    output_data = load_jsonl(output_file)
    
    # Create a mapping from prompt to follow_all_instructions
    # Using prompt text as key for matching
    prompt_to_result = {}
    for item in eval_data:
        prompt = item.get('prompt', '')
        follow_all = item.get('follow_all_instructions', None)
        if prompt:
            prompt_to_result[prompt] = follow_all
    
    # Merge: add 'result' field to output data
    merged_data = []
    matched_count = 0
    unmatched_count = 0
    true_count = 0  # Count of result=true samples
    
    for item in output_data:
        # Try to match by original_prompt
        original_prompt = item.get('original_prompt', '')
        
        if original_prompt in prompt_to_result:
            item['result'] = prompt_to_result[original_prompt]
            matched_count += 1
            # Count true results
            if item['result'] is True:
                true_count += 1
        else:
            # If no exact match, leave result as None
            item['result'] = None
            unmatched_count += 1
        
        merged_data.append(item)
    
    # Save merged data
    save_jsonl(merged_data, result_file)
    
    return len(merged_data), matched_count, unmatched_count, true_count


def main():
    # Define paths
    base_dir = Path(__file__).parent
    ifeval_test_dir = base_dir  # IFEVAL_Test/IFEval
    output_dir = base_dir.parent.parent / "BaseModel_Output" / "IFEVAL"  # BaseModel_Output/IFEVAL
    result_dir = base_dir / "RESULT"
    
    # Create result directory if it doesn't exist
    result_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"IFEval Test Directory: {ifeval_test_dir}")
    print(f"Output Directory: {output_dir}")
    print(f"Result Directory: {result_dir}")
    print("-" * 60)
    
    # Find all model directories containing eval_results_strict.jsonl
    model_dirs = []
    for item in ifeval_test_dir.iterdir():
        if item.is_dir() and item.name != "RESULT":
            eval_file = item / "eval_results_strict.jsonl"
            if eval_file.exists():
                model_dirs.append(item)
    
    print(f"Found {len(model_dirs)} model directories with eval results:")
    for d in model_dirs:
        print(f"  - {d.name}")
    print("-" * 60)
    
    # Process each model
    results_summary = []
    
    for model_dir in model_dirs:
        model_name = model_dir.name
        eval_file = model_dir / "eval_results_strict.jsonl"
        
        # Find matching output file
        output_file = find_matching_output_file(model_name, output_dir)
        
        if output_file is None:
            print(f"[SKIP] {model_name}: No matching output file found")
            continue
        
        # Define result file path
        result_file = result_dir / f"result_{model_name}_IFEVAL_merged.jsonl"
        
        try:
            total, matched, unmatched, true_count = merge_files(eval_file, output_file, result_file)
            # Calculate accuracy (true_count / total)
            accuracy = true_count / total if total > 0 else 0.0
            
            print(f"[OK] {model_name}:")
            print(f"     Total: {total}, Matched: {matched}, Unmatched: {unmatched}")
            print(f"     True: {true_count}, Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
            print(f"     Saved to: {result_file.name}")
            
            results_summary.append({
                'model': model_name,
                'status': 'success',
                'total': total,
                'matched': matched,
                'unmatched': unmatched,
                'true_count': true_count,
                'accuracy': round(accuracy, 4),
                'output_file': str(result_file)
            })
        except Exception as e:
            print(f"[ERROR] {model_name}: {str(e)}")
            results_summary.append({
                'model': model_name,
                'status': 'error',
                'error': str(e)
            })
    
    print("-" * 60)
    print("Processing complete!")
    print(f"Results saved to: {result_dir}")
    
    # Save summary
    summary_file = result_dir / "merge_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, ensure_ascii=False, indent=2)
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()
