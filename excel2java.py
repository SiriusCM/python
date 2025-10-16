import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES  # 改用第三方拖拽库


def get_output_dir():
    """获取正确的输出目录（适配打包后环境）"""
    if getattr(sys, 'frozen', False):
        if sys.platform == 'darwin':  # macOS
            exe_path = os.path.dirname(sys.executable)
            return os.path.abspath(os.path.join(exe_path, '../..'))
        else:  # Windows
            return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def infer_java_type(dtype):
    if 'int' in str(dtype):
        return 'int'
    elif 'float' in str(dtype):
        return 'double'
    else:
        return 'String'


def sanitize_class_name(name):
    if not name:
        return "Sheet"
    name = str(name).strip().replace(' ', '_').replace('-', '_')
    name = ''.join([c if c.isalnum() or c == '_' else '_' for c in name])
    if name and name[0].isdigit():
        name = "S" + name
    if not name:
        name = "Sheet"
    return name


def excel_to_java_classes(excel_path):
    if not os.path.exists(excel_path):
        return f"文件不存在: {excel_path}"

    try:
        excel = pd.ExcelFile(excel_path)
        output_dir = get_output_dir()

        for sheet_name in excel.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1)
            df = df.dropna(axis=1, how='all')
            if df.shape[1] > 0:
                df = df.iloc[:, 1:]

            fields = []
            for col in df.columns:
                if pd.isna(col):
                    continue
                col_type = infer_java_type(df[col].dtype)
                fields.append((str(col), col_type))

            class_name = sanitize_class_name(sheet_name)
            java_code = f"public class {class_name} extends MagusBase {{\n"
            for name, jtype in fields:
                java_code += f"    public {jtype} {name};\n"
            java_code += "}\n"

            output_java_path = os.path.join(output_dir, f"{class_name}.java")
            with open(output_java_path, 'w', encoding='utf-8') as f:
                f.write(java_code)

        return f"已成功处理文件: {excel_path}\nJava文件已生成到: {output_dir}"
    except Exception as e:
        return f"处理文件失败: {excel_path}, 错误: {e}"


def handle_drop(event):
    """处理拖拽文件（使用tkinterdnd2的事件格式）"""
    file_path = event.data.strip().strip('{}').strip('"')
    if os.path.isfile(file_path) and file_path.lower().endswith(('.xlsx', '.xls')):
        result = excel_to_java_classes(file_path)
        messagebox.showinfo("处理结果", result)
    elif file_path:
        messagebox.showerror("错误", f"无效文件: {file_path}")


def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if file_paths:
        for file_path in file_paths:
            result = excel_to_java_classes(file_path)
            messagebox.showinfo("处理结果", result)


if __name__ == "__main__":
    # 使用TkinterDnD替代原生Tk，解决拖拽兼容性问题
    root = TkinterDnD.Tk()
    root.title("Excel 转 Java 类工具")
    root.geometry("400x200")

    # 配置拖拽（第三方库的标准用法）
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', handle_drop)

    # 界面元素
    label = tk.Label(
        root,
        text="将 Excel 文件拖拽到此窗口或点击下面的按钮选择文件",
        font=("Arial", 12),
        wraplength=350
    )
    label.pack(pady=20)

    select_button = tk.Button(root, text="选择文件", command=select_files, width=15, height=2)
    select_button.pack(pady=10)

    root.mainloop()