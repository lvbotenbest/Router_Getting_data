# -*- coding: utf-8 -*-
"""
IFEval Test Script (Python version for Windows)

This script:
1. Runs match_and_eval.py to match prompts and create temporary files
2. Runs IFEval evaluation for each model

Usage:
    python run_ifeval_test.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    base_dir = Path(__file__).parent
    
    print("=" * 50)
    print("Step 1: Running match_and_eval.py")
    print("=" * 50)
    
    # Run the matching script first
    result = subprocess.run(
        [sys.executable, "match_and_eval.py"],
        cwd=base_dir,
        capture_output=False
    )
    
    if result.returncode != 0:
        print("Error: match_and_eval.py failed!")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("Step 2: Running IFEval evaluation for each model")
    print("=" * 50)
    
    # Get all model directories in IFEval folder
    ifeval_dir = base_dir / "IFEval"
    model_dirs = [d for d in ifeval_dir.iterdir() if d.is_dir()]
    
    for model_dir in sorted(model_dirs):
        model_name = model_dir.name
        print()
        print("-" * 50)
        print(f"Evaluating model: {model_name}")
        print("-" * 50)
        
        # Check if required files exist
        input_file = model_dir / "matched_input_data.jsonl"
        response_file = model_dir / "matched_response_data.jsonl"
        
        if not input_file.exists() or not response_file.exists():
            print(f"Warning: Missing files for {model_name}, skipping...")
            continue
        
        # Run evaluation for this model
        result = subprocess.run(
            [
                sys.executable, "-m", "instruction_following_eval.evaluation_main",
                f"--input_data={input_file}",
                f"--input_response_data={response_file}",
                f"--output_dir={model_dir}/"
            ],
            cwd=base_dir,
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"Warning: Evaluation failed for {model_name}")
        else:
            print(f"Evaluation completed for {model_name}")
    
    print()
    print("=" * 50)
    print("All evaluations completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
