import torch
import requests
from torchtext.datasets import IMDB
from torchtext.data import Field, LabelField
import time
import json

# --- 配置 ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"
SAVE_PATH = "teacher_logits.pt"
BATCH_SIZE = 32  # 每次向 Ollama 发送的文本数量
MAX_SAMPLES = 5000  # 限制处理的样本数量（建议至少使用5000以获得更好效果）
# 为了防止log(0)的数值错误，添加一个极小值
EPSILON = 1e-8

# 1. 加载 IMDB 数据集
print("加载 IMDB 数据集...")
# 定义文本和标签的处理方式
TEXT = Field(tokenize='spacy', tokenizer_language='en_core_web_sm', lower=True, batch_first=True)
LABEL = LabelField()

# 加载训练集和测试集
train_data, _ = IMDB.splits(TEXT, LABEL, root='.')

# 构建文本词汇表
TEXT.build_vocab(train_data, max_size=25000)

# 限制样本数量
if MAX_SAMPLES:
    train_data = train_data[:MAX_SAMPLES]

print(f"数据集加载完成，共 {len(train_data)} 个样本。")


# 2. 定义函数向 Ollama 发送请求获取 logits
def get_teacher_logits(texts):
    """
    向本地 Ollama 服务发送文本，获取 gemma3:1b 的情感预测概率。
    将概率转换为 logits (对数概率) 后返回。
    """
    logits_list = []
    for text in texts:
        # 构建请求，明确要求模型返回JSON格式的概率
        prompt = f"""请分析以下文本的情感倾向，并以JSON格式返回'positive'和'negative'的概率。
JSON格式示例: {{ "positive": 0.95, "negative": 0.05 }}
请确保只返回一个纯净的JSON对象，不要包含任何其他解释或文本。

文本:
{text}"""
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)  # 增加超时时间
            response.raise_for_status()
            result_text = response.json().get("response", "")

            # 解析JSON响应
            # 有些模型可能会在JSON前后添加一些无关字符，尝试提取
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_json = json.loads(json_match.group())
            else:
                result_json = json.loads(result_text)

            positive_prob = float(result_json.get("positive", 0.0))
            negative_prob = float(result_json.get("negative", 0.0))

            # 关键修正：将概率转换为 logits
            # 使用 clamp 确保概率在 [EPSILON, 1-EPSILON] 范围内，防止log(0)
            positive_prob = max(EPSILON, min(1.0 - EPSILON, positive_prob))
            negative_prob = max(EPSILON, min(1.0 - EPSILON, negative_prob))

            logits = torch.log(torch.tensor([negative_prob, positive_prob]))

            logits_list.append(logits)
            time.sleep(0.1)  # 避免请求过快

        except Exception as e:
            print(f"获取 logits 失败（文本前50字符：{text[:50]}...）：{e}")
            # 如果失败，返回一个中性的logits
            logits_list.append(torch.log(torch.tensor([0.5, 0.5])))

    return torch.stack(logits_list)


# 3. 批量处理数据并保存
print(f"开始处理 {len(train_data)} 个样本，每次处理 {BATCH_SIZE} 个...")
teacher_logits = []
true_labels = []
texts = []

for i in range(0, len(train_data), BATCH_SIZE):
    # 取一个批次的样本
    batch_samples = train_data[i:i + BATCH_SIZE]
    batch_texts = [example.text for example in batch_samples]  # example.text 是一个单词列表
    raw_texts = [' '.join(example.text) for example in batch_samples]  # 用于显示的原始文本

    # 手动将字符串标签转换为数字张量
    batch_labels = []
    for example in batch_samples:
        if example.label == 'pos':
            batch_labels.append(1.0)
        elif example.label == 'neg':
            batch_labels.append(0.0)
    batch_labels_tensor = torch.tensor(batch_labels, dtype=torch.float)

    # 获取教师模型的 logits
    print(f"  正在处理批次 {i // BATCH_SIZE + 1}...")
    batch_logits = get_teacher_logits(raw_texts)

    # 保存结果
    teacher_logits.append(batch_logits)
    true_labels.append(batch_labels_tensor)
    texts.extend(batch_texts)  # 保存单词列表，用于 student.py 构建词汇表

    print(f"  处理进度：{min(i + BATCH_SIZE, len(train_data))}/{len(train_data)}")

# 合并结果
teacher_logits = torch.cat(teacher_logits)
true_labels = torch.cat(true_labels)

# 保存到本地
torch.save({
    "texts": texts,  # 保存分词后的单词列表
    "true_labels": true_labels,  # 真实标签
    "teacher_logits": teacher_logits  # 教师模型的logits（对数概率）
}, SAVE_PATH)

print(f"\n处理完成！Logits 已保存到 {SAVE_PATH}")
print(f"样本数量：{len(texts)}")
print(f"Logits 形状：{teacher_logits.shape}")
print(f"真实标签形状：{true_labels.shape}")
print(f"示例 Logits (前5个): {teacher_logits[:5]}")