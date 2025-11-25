import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchtext.data import Field

# --- 配置 ---
LOGITS_PATH = "teacher_logits.pt"
STUDENT_MODEL_PATH = "student_model.pth"
VOCAB_SIZE = 25000  # 与脚本一一致
EMBEDDING_DIM = 128
HIDDEN_DIM = 256
NUM_LAYERS = 2
DROPOUT = 0.5
LEARNING_RATE = 1e-3
BATCH_SIZE = 32
EPOCHS = 10
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"使用设备: {DEVICE}")

# 1. 加载数据
print(f"从 {LOGITS_PATH} 加载数据...")
try:
    # 使用 map_location 确保无论模型保存在CPU还是GPU，都能正确加载
    data = torch.load(LOGITS_PATH, map_location=DEVICE)
    texts = data["texts"]
    true_labels = data["true_labels"].to(DEVICE)
    teacher_logits = data["teacher_logits"].to(DEVICE)
    print(f"数据加载成功。样本数: {len(texts)}")
except FileNotFoundError:
    print(f"错误: 找不到文件 {LOGITS_PATH}。请先运行修正后的 teacher.py 生成此文件。")
    exit()

# 2. 构建文本索引和词汇表
print("构建词汇表和文本索引...")
TEXT = Field(sequential=True, batch_first=True, lower=True)

# 直接使用已分词的文本列表构建词汇表
TEXT.build_vocab(texts, max_size=VOCAB_SIZE)
VOCAB_SIZE = len(TEXT.vocab)
print(f"词汇表构建完成，词汇表大小: {VOCAB_SIZE}")

# 将文本（单词列表）转换为索引序列
text_indices = []
for text in texts:
    indices = [TEXT.vocab.stoi.get(word, TEXT.vocab.stoi[TEXT.unk_token]) for word in text]
    text_indices.append(torch.tensor(indices, dtype=torch.long))

# 3. 定义数据集
class SentimentDataset(Dataset):
    def __init__(self, text_indices, true_labels, teacher_logits):
        self.text_indices = text_indices
        self.true_labels = true_labels
        self.teacher_logits = teacher_logits

    def __len__(self):
        return len(self.text_indices)

    def __getitem__(self, idx):
        return self.text_indices[idx], self.true_labels[idx], self.teacher_logits[idx]

# 4. 定义数据加载器（处理变长序列）
def collate_fn(batch):
    texts, labels, logits = zip(*batch)
    texts_padded = nn.utils.rnn.pad_sequence(texts, batch_first=True, padding_value=TEXT.vocab.stoi[TEXT.pad_token])
    labels_stacked = torch.stack(labels)
    logits_stacked = torch.stack(logits)
    return texts_padded, labels_stacked, logits_stacked

dataset = SentimentDataset(text_indices, true_labels, teacher_logits)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
print("数据集和数据加载器准备就绪。")

# 5. 定义学生模型（LSTM 情感分类器）
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

# 初始化模型
model = StudentModel(VOCAB_SIZE, EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS, DROPOUT).to(DEVICE)
print("学生模型初始化完成。")

# 6. 定义蒸馏损失函数
class DistillationLoss(nn.Module):
    def __init__(self, temperature=2.0, alpha=0.5):
        super(DistillationLoss, self).__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()

    def forward(self, student_logits, teacher_logits, true_labels):
        # 蒸馏损失（KL 散度）
        student_softmax = nn.functional.log_softmax(student_logits / self.temperature, dim=-1)
        teacher_softmax = nn.functional.softmax(teacher_logits / self.temperature, dim=-1)
        distillation_loss = nn.functional.kl_div(student_softmax, teacher_softmax.detach(), reduction='batchmean') * (
                    self.temperature ** 2)

        # 真实标签损失
        true_loss = self.ce_loss(student_logits, true_labels.long())

        # 总损失
        return self.alpha * distillation_loss + (1 - self.alpha) * true_loss

loss_fn = DistillationLoss(temperature=2.0, alpha=0.7)
# 引入权重衰减（L2正则化）以防止过拟合
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)

# 7. 训练学生模型
print("开始训练学生模型...")
model.train()
for epoch in range(EPOCHS):
    total_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (texts_padded, labels, teacher_logits_batch) in enumerate(dataloader):
        texts_padded = texts_padded.to(DEVICE)
        labels = labels.to(DEVICE)
        teacher_logits_batch = teacher_logits_batch.to(DEVICE)

        # 前向传播
        student_logits = model(texts_padded)
        loss = loss_fn(student_logits, teacher_logits_batch, labels)

        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 计算损失和准确率
        total_loss += loss.item()
        _, predicted = torch.max(student_logits, 1)
        total += labels.size(0)
        correct += (predicted == labels.long()).sum().item()

        # 打印进度
        if (batch_idx + 1) % 10 == 0:
            batch_acc = correct / total
            print(
                f"Epoch [{epoch + 1}/{EPOCHS}], Batch [{batch_idx + 1}/{len(dataloader)}], Loss: {loss.item():.4f}, Acc: {batch_acc:.4f}")

    # Epoch 统计
    avg_loss = total_loss / len(dataloader)
    avg_acc = correct / total
    print(f"===== Epoch [{epoch + 1}/{EPOCHS}] 结束 =====")
    print(f"平均损失: {avg_loss:.4f}, 平均准确率: {avg_acc:.4f}\n")

# 8. 保存学生模型
torch.save(model.state_dict(), STUDENT_MODEL_PATH)
print(f"学生模型已保存到 {STUDENT_MODEL_PATH}")