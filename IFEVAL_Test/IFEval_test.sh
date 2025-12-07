#!/bin/bash

# IFEval Test Script
# This script:
# 1. Runs match_and_eval.py to match prompts and create temporary files
# 2. Runs IFEval evaluation for each model

echo "=========================================="
echo "Step 1: Running match_and_eval.py"
echo "=========================================="

# Run the matching script first
python match_and_eval.py

if [ $? -ne 0 ]; then
    echo "Error: match_and_eval.py failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Running IFEval evaluation for each model"
echo "=========================================="

# Loop through each model directory in IFEval folder
for model_dir in ./IFEval/*/; do
    if [ -d "$model_dir" ]; then
        model_name=$(basename "$model_dir")
        echo ""
        echo "----------------------------------------"
        echo "Evaluating model: $model_name"
        echo "----------------------------------------"
        
        # Run evaluation for this model
        python -m instruction_following_eval.evaluation_main \
            --input_data="${model_dir}matched_input_data.jsonl" \
            --input_response_data="${model_dir}matched_response_data.jsonl" \
            --output_dir="${model_dir}"
        
        if [ $? -ne 0 ]; then
            echo "Warning: Evaluation failed for $model_name"
        else
            echo "Evaluation completed for $model_name"
        fi
    fi
done

echo ""
echo "=========================================="
echo "All evaluations completed!"
echo "=========================================="