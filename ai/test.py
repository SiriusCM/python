import tkinter as tk
from PIL import Image, ImageDraw
import torch
from torchvision import transforms


# --- 1. 模型定义 ---
# 必须先定义模型结构，否则无法加载权重
class VisionModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(28 * 28, 64)
        self.fc2 = torch.nn.Linear(64, 64)
        self.fc3 = torch.nn.Linear(64, 64)
        self.fc4 = torch.nn.Linear(64, 10)

    def forward(self, x):
        x = torch.nn.functional.relu(self.fc1(x))
        x = torch.nn.functional.relu(self.fc2(x))
        x = torch.nn.functional.relu(self.fc3(x))
        x = torch.nn.functional.log_softmax(self.fc4(x), dim=1)
        return x


# --- 2. 图像预处理 ---
def preprocess_image(image):
    """将PIL图像预处理成模型所需的28x28灰度张量"""
    preprocess = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
    ])
    img_tensor = preprocess(image)
    # 反色，因为我们是白底黑字，而MNIST是黑底白字
    img_tensor = 1 - img_tensor
    # 展平并增加批次维度 (batch_size, 784)
    return img_tensor.view(-1, 28 * 28)


# --- 3. 手写绘画板应用 ---
class HandwritingRecognitionApp:
    def __init__(self, root, model_path="visionModel_dict.pth"):
        self.root = root
        self.root.title("手写数字识别器")

        # 加载模型
        self.device = torch.device("cpu")
        self.model = VisionModel().to(self.device)
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()  # 设置为评估模式
            status_text = "模型加载成功！"
        except FileNotFoundError:
            status_text = f"错误：未找到模型文件 '{model_path}'。"
            self.model = None  # 模型加载失败

        # UI组件
        self.canvas_width = 280
        self.canvas_height = 280
        self.brush_size = 6

        # 画布
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white",
                                highlightthickness=1, highlightbackground="grey")
        self.canvas.pack(pady=20, padx=20)

        # 用于保存绘制内容的PIL图像
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        # 控制按钮框架
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        self.clear_btn = tk.Button(control_frame, text="清除", command=self.clear_canvas, font=("Arial", 12))
        self.clear_btn.grid(row=0, column=0, padx=10)

        self.predict_btn = tk.Button(control_frame, text="识别", command=self.predict_digit, font=("Arial", 12))
        self.predict_btn.grid(row=0, column=1, padx=10)

        # 状态和结果显示
        self.status_label = tk.Label(root, text=status_text, font=("Arial", 12), fg="green" if self.model else "red")
        self.status_label.pack(pady=5)

        self.result_label = tk.Label(root, text="请在画板上书写数字", font=("Arial", 16))
        self.result_label.pack(pady=10)

        # 绑定鼠标绘图事件
        self.canvas.bind("<B1-Motion>", self.draw_on_canvas)

    def draw_on_canvas(self, event):
        """在画布和PIL图像上同时绘制"""
        if self.model is None: return  # 如果模型未加载，则不允许绘制

        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline="black")
        self.draw.ellipse((x1, y1, x2, y2), fill="black")

    def clear_canvas(self):
        """清空画布"""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.result_label.config(text="请在画板上书写数字", fg="black")

    def predict_digit(self):
        """使用加载的模型识别绘制的数字"""
        if self.model is None:
            self.result_label.config(text="模型未加载，无法识别！", fg="red")
            return

        img_tensor = preprocess_image(self.image)

        with torch.no_grad():
            output = self.model(img_tensor.to(self.device))
            pred = torch.argmax(output).item()

        self.result_label.config(text=f"识别结果: {pred}", fg="blue")


# --- 4. 运行应用 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = HandwritingRecognitionApp(root)
    root.mainloop()