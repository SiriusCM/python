import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def infer_java_type(dtype):
    if 'int' in str(dtype):
        return 'int'
    elif 'float' in str(dtype):
        return 'double'
    else:
        return 'String'


def sanitize_class_name(name):
    # 将工作表名转换为合法的 Java 类名
    if not name:
        return "Sheet"
    # 去掉非法字符，首字符如果是数字则添加前缀
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
        for sheet_name in excel.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1)

            # 去掉全空列
            df = df.dropna(axis=1, how='all')

            # 去掉第一列
            if df.shape[1] > 0:
                df = df.iloc[:, 1:]

            # 获取列名和推断类型
            fields = []
            for col in df.columns:
                if pd.isna(col):
                    continue
                col_type = infer_java_type(df[col].dtype)
                fields.append((str(col), col_type))

            # 生成 Java 代码
            class_name = sanitize_class_name(sheet_name)
            java_code = f"public class {class_name} extends MagusBase {{\n"
            for name, jtype in fields:
                java_code += f"    public {jtype} {name};\n"
            java_code += "}\n"

            # 输出到同级目录
            output_dir = os.path.dirname(os.path.abspath(__file__))
            output_java_path = os.path.join(output_dir, f"{class_name}.java")

            with open(output_java_path, 'w', encoding='utf-8') as f:
                f.write(java_code)

        return f"已成功处理文件: {excel_path}"
    except Exception as e:
        return f"处理文件失败: {excel_path}, 错误: {e}"


def handle_drop(event):
    file_paths = event.data.strip().split(" ")
    for file_path in file_paths:
        file_path = file_path.strip('"')
        if os.path.isfile(file_path) and file_path.endswith(('.xlsx', '.xls')):
            result = excel_to_java_classes(file_path)
            messagebox.showinfo("处理结果", result)
        else:
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

# 允许窗口接收文件拖拽
root.bind("<B1-Motion>", lambda event: None)
root.bind("<<Drop>>", handle_drop)

label = tk.Label(root, text="将 Excel 文件拖拽到此窗口或点击下面的按钮选择文件", font=("Arial", 12))
label.pack(pady=20)

select_button = tk.Button(root, text="选择文件", command=select_files)
select_button.pack(pady=10)

root.mainloop()