# IFEval 测试指南

本文档介绍如何运行 IFEval (Instruction Following Evaluation) 测试并合并结果。

## 📁 目录结构

```
IFEVAL_Test/
├── IFEval/                           # IFEval 测试目录
│   ├── <model_name>/                 # 各模型的测试结果目录
│   │   ├── matched_input_data.jsonl  # 匹配后的输入数据
│   │   ├── matched_response_data.jsonl # 匹配后的响应数据
│   │   ├── eval_results_strict.jsonl # 严格模式评估结果
│   │   └── eval_results_loose.jsonl  # 宽松模式评估结果
│   └── RESULT/                       # 合并后的最终结果
│       ├── result_<model>_IFEVAL_merged.jsonl  # 各模型合并结果
│       └── merge_summary.json        # 汇总统计报告
├── instruction_following_eval/       # IFEval 评估库
├── match_and_eval.py                 # 数据匹配脚本
├── run_ifeval_test.py                # Python 版测试脚本 (Windows)
├── IFEval_test.sh                    # Bash 版测试脚本 (Linux/Mac)
└── README_IFEval.md                  # 本文档
```

## 🚀 运行步骤

### 前置条件

1. 确保已安装 Python 3.8+
2. 确保 `BaseModel_Output/IFEVAL/` 目录下有各模型的输出文件：
   - 格式：`result_<model_name>_IFEVAL.jsonl`

### Step 1: 运行 IFEval 测试

#### Windows 系统

```bash
cd IFEVAL_Test
python run_ifeval_test.py
```

#### Linux/Mac 系统

```bash
cd IFEVAL_Test
chmod +x IFEval_test.sh
./IFEval_test.sh
```

**测试流程说明：**

1. **Step 1**: 运行 `match_and_eval.py`
   - 读取 `BaseModel_Output/IFEVAL/` 下的模型输出文件
   - 与 IFEval 原始数据集进行 prompt 匹配
   - 为每个模型生成 `matched_input_data.jsonl` 和 `matched_response_data.jsonl`

2. **Step 2**: 对每个模型运行 IFEval 评估
   - 使用 `instruction_following_eval` 库进行评估
   - 生成 `eval_results_strict.jsonl` (严格模式) 和 `eval_results_loose.jsonl` (宽松模式)

### Step 2: 合并结果

测试完成后，运行合并脚本将评估结果与原始输出合并：

```bash
cd IFEVAL_Test/IFEval
python merge_eval_results.py
```

**合并脚本功能：**

- 将 `eval_results_strict.jsonl` 中的 `follow_all_instructions` 字段
- 以 `result` 为键名添加到原始输出文件中
- 计算每个模型的正确率 (accuracy)
- 生成汇总报告 `merge_summary.json`

## 📊 输出结果

### 合并后的 JSONL 文件

每个模型生成一个 `result_<model_name>_IFEVAL_merged.jsonl` 文件，包含以下字段：

| 字段 | 说明 |
|------|------|
| `id` | 样本 ID |
| `model` | 模型名称 |
| `dataset` | 数据集名称 (IFEVAL) |
| `original_prompt` | 原始 prompt |
| `response` | 模型响应 |
| `cost` | API 调用成本 |
| `instruction_id_list` | 指令 ID 列表 |
| `kwargs` | 指令参数 |
| `result` | **评估结果** (true/false) - 是否遵循所有指令 |

### 汇总报告 (merge_summary.json)

包含每个模型的统计信息：

```json
{
  "model": "模型名称",
  "status": "success",
  "total": 1500,        // 总样本数
  "matched": 1497,      // 匹配成功数
  "unmatched": 3,       // 未匹配数
  "true_count": 1280,   // 正确数 (result=true)
  "accuracy": 0.8533,   // 正确率
  "output_file": "输出文件路径"
}
```

## 📈 评估指标

- **Accuracy (正确率)**: `true_count / total`
- 表示模型在所有样本中，完全遵循所有指令的比例
- 严格模式 (strict) 要求精确匹配所有指令约束

## ⚠️ 注意事项

1. **文件命名**: 模型输出文件必须遵循 `result_<model_name>_IFEVAL.jsonl` 格式
2. **Prompt 匹配**: 合并时使用 `original_prompt` 与 `prompt` 进行精确匹配
3. **未匹配样本**: 少量样本可能因 prompt 微小差异导致未匹配，其 `result` 字段为 `null`

## 🔧 故障排除

### 问题: 模型目录为空

确保已运行 `match_and_eval.py` 生成匹配文件。

### 问题: 评估失败

检查 `instruction_following_eval` 库是否正确安装：
```bash
pip install -e instruction_following_eval/
```

### 问题: 合并时匹配率低

检查 prompt 是否在生成模型响应时被修改。
