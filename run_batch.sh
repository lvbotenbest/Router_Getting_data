#!/bin/bash

# --- 1. 定义要跑的模型列表 ---
MODELS=(
    "deepseek-ai/DeepSeek-V3.2-Exp"
    "Qwen/Qwen3-235B-A22B-Instruct-2507"
    "openai/gpt-oss-120b"
    "google/gemma-3-27b-it"
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
    "google/gemma-3-12b-it"
    "moonshotai/Kimi-K2-Instruct-0905"
    "deepseek-ai/DeepSeek-V3.1-Terminus"

)



# --- 2. 定义数据集列表 ---
DATASETS=(
    # "GSM8k"
    "MMLU_PRO"
    # "GSM8k_Test"
    # "IFEVAL"
    #"BBH"
    # "Human_Eval"
)

# --- 3. 配置并发控制 ---
MAX_JOBS=100   # 同时运行的最大 Python 进程数
LOG_FILE="log/master_run_BBH.log" # 总日志文件

echo "========== 开始批量评测任务 ==========" > $LOG_FILE
echo "时间: $(date)" >> $LOG_FILE

# --- 4. 循环调度 ---
for model in "${MODELS[@]}"; do
    for dataset in "${DATASETS[@]}"; do
        
        # (并发控制核心逻辑)
        # 检查当前后台任务数量，如果 >= MAX_JOBS，则等待
        while [ $(jobs -r | wc -l) -ge $MAX_JOBS ]; do
            sleep 1
        done

        echo "正在启动: Model [$model] on Dataset [$dataset]"
        
        # 使用临时日志文件缓存输出，任务完成后统一写入主日志，避免乱序
        mkdir -p log/temp
        safe_model_name=$(echo "$model" | tr '/' '_')
        TEMP_LOG="log/temp/${safe_model_name}_${dataset}.log"
        
        (
            # 执行 Python 脚本，日志先写入临时文件
            python api_worker.py --model "$model" --dataset "$dataset" --concurrency 20 > "$TEMP_LOG" 2>&1
            
            # 任务结束后，将临时日志内容追加到主日志文件
            # 注意：这里假设 cat 操作足够快，并发冲突概率低
            cat "$TEMP_LOG" >> "$LOG_FILE"
            
            # 删除临时文件
            rm "$TEMP_LOG"
        ) &
        
    done
done

# --- 5. 等待所有任务结束 ---
echo "所有任务已派发，正在等待运行结束..."
wait

echo "========== 所有评测任务已全部完成 ==========" >> $LOG_FILE
echo "========== 所有评测任务已全部完成 =========="