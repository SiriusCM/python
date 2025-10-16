import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def get_output_dir():
    """获取正确的输出目录（适配打包后环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境（PyInstaller）
        if sys.platform == 'darwin':  # macOS
            # 获取程序所在目录（.app 包的上层目录）
            exe_path = os.path.dirname(sys.executable)
            # macOS 下 .app 内部路径为 .../Contents/MacOS/，需返回上两级到 .app 所在目录
            return os.path.abspath(os.path.join(exe_path, '../..'))
        else:  # Windows
            return os.path.dirname(sys.executable)
    else:
        # 未打包的开发环境
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
        # 获取正确的输出目录（关键修复）
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
    # 修复macOS下拖拽路径包含空格的问题
    file_paths = event.data.split('\n')  # macOS 拖拽路径用换行分隔
    for file_path in file_paths:
        file_path = file_path.strip().strip('"')
        if os.path.isfile(file_path) and file_path.lower().endswith(('.xlsx', '.xls')):
            result = excel_to_java_classes(file_path)
            messagebox.showinfo("处理结果", result)
        elif file_path:  # 忽略空字符串
            messagebox.showerror("错误", f"无效文件: {file_path}")


def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if file_paths:
        for file_path in file_paths:
            result = excel_to_java_classes(file_path)
            messagebox.showinfo("处理结果", result)


root = tk.Tk()
root.title("Excel 转 Java 类工具")
root.geometry("400x200")

# 配置拖拽支持（适配macOS）
root.drop_target_register(tk.DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)

label = tk.Label(root, text="将 Excel 文件拖拽到此窗口或点击下面的按钮选择文件", font=("Arial", 12))
label.pack(pady=20)

select_button = tk.Button(root, text="选择文件", command=select_files)
select_button.pack(pady=10)

root.mainloop()