# Construct_Dataset

用于构建大型语言模型 (LLM) 评估数据集的工具集。本项目支持多个模型在多个基准数据集上进行批量推理和评估。

## 📁 项目结构

```
Construct_Dataset/
├── Dataset/                          # 原始数据集
│   ├── GSM8k/                        # 数学推理数据集
│   ├── MMLU_PRO/                     # 多任务语言理解数据集
│   ├── BBH/                          # Big-Bench Hard 数据集
│   ├── IFEVAL/                       # 指令遵循评估数据集
│   ├── HumanEval/                    # 代码生成数据集
│   └── NQ/                           # Natural Questions 数据集
│
├── BaseModel_Output/                 # 模型推理输出结果
│   ├── GSM8k/                        # 各模型在 GSM8k 上的输出
│   ├── MMLU_PRO/                     # 各模型在 MMLU_PRO 上的输出
│   ├── BBH/                          # 各模型在 BBH 上的输出
│   ├── IFEVAL/                       # 各模型在 IFEVAL 上的输出
│   ├── Human_Eval/                   # 各模型在 HumanEval 上的输出
│   └── GSM8k_Test/                   # 各模型在 GSM8k 测试集上的输出
│
├── IFEVAL_Test/                      # IFEval 评估模块
│   ├── IFEval/                       # 评估结果和合并数据
│   ├── instruction_following_eval/   # IFEval 评估库
│   ├── run_ifeval_test.py            # 运行评估 (Windows)
│   ├── IFEval_test.sh                # 运行评估 (Linux/Mac)
│   ├── match_and_eval.py             # 数据匹配脚本
│   └── README_IFEval.md              # IFEval 使用文档
│
├── human-eval/                       # HumanEval 评估模块
│
├── log/                              # 运行日志目录
│
├── api_worker.py                     # 核心: API 批量推理脚本
├── api_worker_single_request.py      # 单请求版本推理脚本
├── dataset_templates.py              # 数据集 prompt 模板管理
├── run_batch.sh                      # 批量运行脚本
├── run_batch_pre.sh                  # 预处理批量脚本
└── test_template.py                  # 模板测试脚本
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 安装依赖
pip install openai

# 设置 API 密钥 (在 api_worker.py 中配置)
API_KEY = "your-api-key"
BASE_URL = "your-api-base-url"
```

### 2. 运行模型推理

#### 单个模型-数据集组合

```bash
python api_worker.py --model "deepseek-ai/DeepSeek-V3.1-Terminus" --dataset "GSM8k" --concurrency 20
```

#### 批量运行所有模型

```bash
# Linux/Mac
chmod +x run_batch.sh
./run_batch.sh

# Windows
# 修改 run_batch.sh 中的模型和数据集列表，然后使用 Git Bash 运行
```

### 3. 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--model` | 模型名称 | `deepseek-ai/DeepSeek-V3.1-Terminus` |
| `--dataset` | 数据集名称 | `GSM8k`, `MMLU_PRO`, `IFEVAL`, `BBH`, `Human_Eval` |
| `--concurrency` | 并发请求数 | `20` |

## 📊 支持的数据集

| 数据集 | 描述 | 评估指标 |
|--------|------|----------|
| **GSM8k** | 小学数学推理问题 | 准确率 (Accuracy) |
| **MMLU_PRO** | 多任务语言理解 (专业版) | 准确率 (Accuracy) |
| **BBH** | Big-Bench Hard 困难推理任务 | 准确率 (Accuracy) |
| **IFEVAL** | 指令遵循评估 | 严格/宽松准确率 |
| **HumanEval** | Python 代码生成 | Pass@k |
| **NQ** | Natural Questions 问答 | F1/EM |

## 🤖 支持的模型

当前配置支持的模型列表 (可在 `api_worker.py` 中扩展):

- `deepseek-ai/DeepSeek-V3.1-Terminus`
- `deepseek-ai/DeepSeek-V3.2-Exp`
- `Qwen/Qwen3-235B-A22B-Instruct-2507`
- `openai/gpt-oss-120b`
- `google/gemma-3-27b-it`
- `google/gemma-3-12b-it`
- `mistralai/Mistral-Small-3.2-24B-Instruct-2506`
- `moonshotai/Kimi-K2-Instruct-0905`

## 📤 输出格式

每个模型-数据集组合生成一个 JSONL 文件:

**路径**: `BaseModel_Output/<DATASET>/result_<model_name>_<DATASET>.jsonl`

**示例**: `BaseModel_Output/IFEVAL/result_deepseek-ai_DeepSeek-V3.1-Terminus_IFEVAL.jsonl`

**字段说明**:

```json
{
  "id": 1000,
  "model": "deepseek-ai/DeepSeek-V3.1-Terminus",
  "dataset": "IFEVAL",
  "original_prompt": "原始问题/指令",
  "response": "模型生成的响应",
  "cost": 0.00050028,
  "instruction_id_list": ["..."],
  "kwargs": [...]
}
```

## 🧪 评估流程

### IFEval 评估

```bash
cd IFEVAL_Test

# Step 1: 运行评估
python run_ifeval_test.py

# Step 2: 合并结果并计算正确率
cd IFEval
python merge_eval_results.py
```

详细说明请参阅 [IFEVAL_Test/README_IFEval.md](IFEVAL_Test/README_IFEval.md)

### HumanEval 评估

```bash
cd human-eval
python test_for_human_eval.py
```

## 📈 结果汇总

评估完成后，各数据集的结果汇总:

| 位置 | 内容 |
|------|------|
| `IFEVAL_Test/IFEval/RESULT/merge_summary.json` | IFEval 各模型正确率 |
| `BaseModel_Output/<DATASET>/` | 各数据集的模型原始输出 |

## ⚙️ 配置说明

### 价格配置 (api_worker.py)

```python
PRICES = {
    "deepseek-ai/DeepSeek-V3.1-Terminus": {"in": 0.21, "out": 0.79},
    "google/gemma-3-12b-it": {"in": 0.04, "out": 0.13},
    # 添加更多模型...
}
```

### 数据集路径配置

```python
DATASET_MAPPING = {
    "GSM8k": "Dataset/GSM8k/train.cleand.jsonl",
    "MMLU_PRO": "Dataset/MMLU_PRO/mmlupro.jsonl",
    "IFEVAL": "Dataset/IFEVAL/ifeval_input_data.jsonl",
    # 添加更多数据集...
}
```

## 📝 日志

运行日志保存在 `log/` 目录下:
- `master_run_<DATASET>.log` - 主日志文件
- `log/temp/` - 临时日志 (运行完成后自动清理)

## 🔧 故障排除

### 问题: API 请求失败

脚本内置重试机制 (2s → 30s → Fail)，如果仍然失败:
- 检查 API 密钥和 URL 配置
- 检查网络连接
- 降低并发数 (`--concurrency`)

### 问题: 输出文件为空

- 确保数据集文件存在于 `Dataset/` 目录
- 检查数据集路径映射是否正确

### 问题: 评估脚本报错

- 确保已先运行推理生成输出文件
- 检查 `BaseModel_Output/<DATASET>/` 目录下是否有对应文件

## 📄 License

MIT License
