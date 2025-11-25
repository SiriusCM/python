import torch
import torch.nn as nn
import gradio as gr
from torchtext.data import Field
import spacy

# --- 配置 ---
STUDENT_MODEL_PATH = "student_model.pth"
VOCAB_SIZE = 25000  # 与脚本一、二一致
EMBEDDING_DIM = 128
HIDDEN_DIM = 256
NUM_LAYERS = 2
DROPOUT = 0.5
MAX_SEQ_LEN = 128  # 最大序列长度
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"使用设备: {DEVICE}")

# 1. 加载分词器和词汇表
print("加载分词器和词汇表...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("找不到 'en_core_web_sm' 模型，正在尝试下载...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

TEXT = Field(tokenize='spacy', tokenizer_language='en_core_web_sm', lower=True, batch_first=True)

# 修正：直接使用从文件中加载的、已经分词好的文本列表来构建词汇表
try:
    # 加载文本数据用于构建词汇表
    # 使用 map_location=DEVICE 避免在 CPU 上加载 CUDA 张量时出错
    texts_data = torch.load("teacher_logits.pt", map_location=DEVICE)["texts"]
    TEXT.build_vocab(texts_data, max_size=VOCAB_SIZE)
    VOCAB_SIZE = len(TEXT.vocab)
    print(f"词汇表构建完成，词汇表大小: {VOCAB_SIZE}")
except FileNotFoundError:
    print(f"错误: 找不到文件 'teacher_logits.pt'。请确保该文件与脚本在同一目录下。")
    exit()

# 2. 定义学生模型（与脚本二完全一致）
class StudentModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers, dropout):
        super(StudentModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True,
                            dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, 2)  # 输出 2 个类（负面/正面）
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # x: (batch_size, seq_len)
        embedded = self.dropout(self.embedding(x))  # (batch_size, seq_len, embedding_dim)
        lstm_out, (hidden, cell) = self.lstm(embedded)  # (batch_size, seq_len, hidden_dim)
        # 使用最后一个时间步的输出
        out = self.fc(self.dropout(hidden[-1]))  # (batch_size, 2)
        return out

# 3. 加载学生模型
print(f"从 {STUDENT_MODEL_PATH} 加载学生模型...")
try:
    model = StudentModel(VOCAB_SIZE, EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS, DROPOUT).to(DEVICE)
    # 使用 map_location=DEVICE 确保模型权重加载到正确的设备上
    model.load_state_dict(torch.load(STUDENT_MODEL_PATH, map_location=DEVICE))
    model.eval()  # 设置为评估模式
    print("模型加载成功。")
except FileNotFoundError:
    print(f"错误: 找不到模型文件 '{STUDENT_MODEL_PATH}'。请确保该文件与脚本在同一目录下。")
    exit()
except Exception as e:
    print(f"加载模型时发生错误: {e}")
    exit()

# 4. 定义情感预测函数
def predict_sentiment(text):
    """
    预测文本的情感（正面/负面）。
    """
    if not text.strip():
        return "请输入有效的文本。"

    # 文本预处理：分词
    tokens = [token.text for token in nlp(text.lower())]

    # 转换为索引序列
    indices = [TEXT.vocab.stoi.get(token, TEXT.vocab.stoi["<unk>"]) for token in tokens]

    # 截断或填充到最大长度
    if len(indices) > MAX_SEQ_LEN:
        indices = indices[:MAX_SEQ_LEN]
    else:
        indices += [TEXT.vocab.stoi["<pad>"]] * (MAX_SEQ_LEN - len(indices))

    # 转换为张量并添加 batch 维度
    x = torch.tensor(indices, dtype=torch.long).unsqueeze(0).to(DEVICE)  # 形状: (1, MAX_SEQ_LEN)

    # 模型预测
    with torch.no_grad():  # 关闭梯度计算，节省资源
        logits = model(x)
        probabilities = nn.functional.softmax(logits, dim=-1)
        negative_prob = probabilities[0][0].item()
        positive_prob = probabilities[0][1].item()

    # 输出结果
    if positive_prob > negative_prob:
        sentiment = "正面"
        confidence = positive_prob
    else:
        sentiment = "负面"
        confidence = negative_prob

    return (f"情感预测：{sentiment}\n"
            f"负面概率：{negative_prob:.4f}\n"
            f"正面概率：{positive_prob:.4f}\n"
            f"置信度：{confidence:.4f}")

# 5. 使用 Gradio 构建网页
print("启动 Gradio 网页...")
with gr.Blocks() as demo:
    gr.Markdown(
        """
        # 情感分析学生模型交互演示
        输入一段英文文本，模型会预测其情感是正面还是负面。
        模型基于 gemma3:1b 蒸馏训练而成。
        """
    )
    input_text = gr.Textbox(label="输入文本", placeholder="请输入英文文本...", lines=3)
    output_text = gr.Textbox(label="预测结果", lines=5)
    submit_btn = gr.Button("预测", variant="primary")

    submit_btn.click(predict_sentiment, inputs=input_text, outputs=output_text)

# 启动网页
# server_name="0.0.0.0" 允许局域网内其他设备访问
demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)