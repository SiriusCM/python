import websocket
import json
import os
from typing import Dict, List
import re

# -------------------------- 核心配置（可按需修改） --------------------------
WS_URL = "ws://unified-admin.jd.com/excel"
REQUEST_PARAMS = {
    "url": "/excel/cs/sheet/getAll",
    "gameCode": "7fresh"
}
JAVA_PACKAGE = "com.jdt.bootstrap.magus.client.conf"  # Java 包名
CONFIG_BASE_CLASS = "ConfigBase"  # 父类名（与项目一致）
SAVE_DIR = "./generated_java"  # Java 文件保存根目录（默认当前目录下 generated_java）

# -------------------------- 类型映射（Python → Java） --------------------------
TYPE_MAPPING = {
    str: "String",
    int: "Integer",
    float: "Double",
    list: "List",
    dict: "Map<String, Object>",
    bool: "Boolean"
}

# -------------------------- 工具函数 --------------------------
def camel_to_pascal(camel_str: str) -> str:
    """驼峰命名 → 帕斯卡命名（首字母大写）"""
    if not camel_str:
        return camel_str
    return camel_str[0].upper() + camel_str[1:]

def get_java_field_type(python_value) -> str:
    """根据 Python 值推断 Java 字段类型"""
    if isinstance(python_value, list):
        if not python_value:
            return "List<Object>"
        elem_type = TYPE_MAPPING.get(type(python_value[0]), "Object")
        return f"List<{elem_type}>"
    return TYPE_MAPPING.get(type(python_value), "String")

def get_index_field(data_list: List[Dict]) -> str:
    """推断索引字段（优先 id/itemSn/sn，无则取第一个字段）"""
    if not data_list:
        return "id"
    priority_fields = ["id", "itemSn", "sn"]
    for field in priority_fields:
        if field in data_list[0]:
            return field
    return list(data_list[0].keys())[0]

def create_package_dir(save_root: str, package: str) -> str:
    """根据 Java 包名创建目录结构（如 com/jdt/bootstrap/magus/client/conf）"""
    package_dir = os.path.join(save_root, package.replace(".", os.sep))
    os.makedirs(package_dir, exist_ok=True)  # 不存在则创建，已存在不报错
    return package_dir

# -------------------------- WebSocket 数据请求 --------------------------
def fetch_websocket_data() -> Dict[str, List[Dict]]:
    """连接 WebSocket 并获取解析后的结构化数据"""
    print(f"🔄 正在连接 {WS_URL}...")
    data_store = {}

    def on_open(ws):
        print("✅ WebSocket 连接成功，发送请求...")
        ws.send(json.dumps(REQUEST_PARAMS))

    def on_message(ws, message):
        print("📥 收到响应，解析数据...")
        response = json.loads(message)
        # 解析嵌套的 JSON 字符串
        for sheet_name, json_str in response["sheetDataMap"].items():
            data_store[sheet_name] = json.loads(json_str)
        ws.close()  # 数据获取完成关闭连接

    def on_error(ws, error):
        print(f"❌ WebSocket 错误：{error}")
        raise Exception(f"WebSocket 请求失败：{error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"🔌 连接关闭：状态码 {close_status_code}")

    # 启动 WebSocket 连接（携带认证 Cookie）
    ws = websocket.WebSocketApp(
        WS_URL,
        header={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": "your_jd_cookie=xxx; sessionId=xxx"  # 替换为你的实际 Cookie
        },
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(ping_interval=30)

    if not data_store:
        raise Exception("❌ 未获取到有效数据")
    print(f"✅ 数据解析完成，共 {len(data_store)} 类配置：{list(data_store.keys())}\n")
    return data_store

# -------------------------- Java 类生成与文件写入 --------------------------
def generate_and_save_java_class(sheet_name: str, data_list: List[Dict], save_dir: str):
    """生成 Java 类并保存为 .java 文件"""
    if not data_list:
        print(f"⚠️ {sheet_name} 无数据，跳过文件生成")
        return

    # 1. 构建类名、索引字段、字段定义
    class_name = f"Conf{camel_to_pascal(sheet_name)}"
    index_field = get_index_field(data_list)
    fields = data_list[0].keys()

    # 2. 生成内部 Data 类字段
    data_fields = []
    for field in fields:
        field_value = data_list[0][field]
        java_type = get_java_field_type(field_value)
        data_fields.append(f"    /** 类型：{type(field_value).__name__} */")
        data_fields.append(f"    private {java_type} {field};")
    data_fields_str = "\n".join(data_fields)

    # 3. 拼接完整 Java 代码
    java_code = f"""package {JAVA_PACKAGE};

import lombok.Data;
import lombok.EqualsAndHashCode;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;

/**
 * {sheet_name} 配置类（自动生成）
 * 对应 WebSocket 返回值中的 {sheet_name} 数据
 * 生成时间：自动生成，请勿手动修改
 */
@MagusConfig(
    gameCode = "{REQUEST_PARAMS['gameCode']}",
    sheetName = "{sheet_name}",
    indexName = "{index_field}"
)
@Service
public class {class_name} extends {CONFIG_BASE_CLASS} {{

    @EqualsAndHashCode(callSuper = true)
    @Data
    public static class Data extends {CONFIG_BASE_CLASS}.BaseData {{
{data_fields_str}
    }}
}}
"""

    # 4. 写入文件
    file_name = f"{class_name}.java"
    file_path = os.path.join(save_dir, file_name)
    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(java_code)
    print(f"📁 已生成文件：{file_path}")

# -------------------------- 主流程 --------------------------
def main():
    try:
        # 1. 从 WebSocket 获取结构化数据
        structured_data = fetch_websocket_data()

        # 2. 创建包目录结构（根据 Java 包名）
        package_dir = create_package_dir(SAVE_DIR, JAVA_PACKAGE)
        print(f"📂 文件保存目录：{package_dir}\n")

        # 3. 生成并保存所有 Java 文件
        print("🚀 开始生成 Java 文件...")
        for sheet_name, data_list in structured_data.items():
            generate_and_save_java_class(sheet_name, data_list, package_dir)

        # 4. 输出执行结果
        print("\n" + "=" * 80)
        print("🎉 执行成功！")
        print(f"✅ 共生成 {len(structured_data)} 个 Java 文件")
        print(f"✅ 文件保存路径：{package_dir}")
        print("✅ 可直接将 generated_java 目录下的包结构复制到 Java 项目 src/main/java 目录")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 执行失败：{str(e)}")

if __name__ == "__main__":
    main()