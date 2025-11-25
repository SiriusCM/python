# generate_universal_distillation_data.py
import requests
import json
import time
from datasets import load_dataset

# --- 配置 ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"
OUTPUT_FILE = "universal_distillation_data.jsonl"
DATASET_NAME = "google/flan_v2"  # 或者 "bigscience/P3"
NUM_SAMPLES = 1000  # 你想生成的数据量


def get_teacher_response(prompt):
    """调用 Ollama API 获取教师模型的响应"""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.5}  # 温度可以调低一点，让输出更稳定
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)  # 延长超时时间
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error generating response for prompt '{prompt[:50]}...': {e}")
        return None


def main():
    print(f"Loading dataset: {DATASET_NAME}")
    # 加载数据集，这里我们只取 'train'  split 的一小部分
    dataset = load_dataset(DATASET_NAME, split="train[:10000]")  # 先加载10000条，避免内存问题

    print(f"Generating {NUM_SAMPLES} teacher responses...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        generated_count = 0
        for item in dataset:
            if generated_count >= NUM_SAMPLES:
                break

            # FLAN 数据集的 'input' 字段就是我们需要的 prompt
            prompt = item.get("input", "")

            # 有些任务可能需要结合 'instruction' 和 'input'
            if "instruction" in item and item["instruction"]:
                prompt = f"{item['instruction']}\n{prompt}".strip()

            if not prompt:
                continue

            print(f"Generating response for prompt {generated_count + 1}/{NUM_SAMPLES}: '{prompt[:60]}...'")

            teacher_response = get_teacher_response(prompt)

            if teacher_response:
                # 保存 (prompt, response) 对
                data_point = {
                    "prompt": prompt,
                    "teacher_response": teacher_response
                }
                f_out.write(json.dumps(data_point) + "\n")
                generated_count += 1

            # 避免请求过快
            time.sleep(0.5)

    print(f"Done! {generated_count} samples saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()