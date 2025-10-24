import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import pymysql
from pymysql import OperationalError
import tkinter as tk  # 导入Tkinter库


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


def get_time_thresholds():
    """用Python计算7天前0点和3天前0点的时间戳（秒级）"""
    # 获取当前日期的0点（今天0:00:00）
    today_zero = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # 7天前0点
    seven_days_ago_zero = today_zero - timedelta(days=7)
    # 3天前0点
    three_days_ago_zero = today_zero - timedelta(days=3)
    # 转换为Unix时间戳（秒级）
    return int(seven_days_ago_zero.timestamp()), int(three_days_ago_zero.timestamp())


def query_server(server_id, host, port, seven_days_ts, three_days_ts):
    """查询单个服务器数据，使用Python计算的时间戳作为条件"""
    result = {
        "服务器序号": server_id,
        "7天前至今": None,
        "3天前至今": None,
        "10级": None,
        "30级": None,
        "80级": None,
        "130级": None,
    }

    # 数据库连接参数
    db_config = {
        "host": host,
        "port": port,
        "user": "root",
        "password": "tudoudaxia",
        "db": "bl_s1",
        "charset": "utf8mb4",
        "connect_timeout": 1
    }

    conn = None
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # SQL使用Python计算的时间戳，避免依赖MySQL的时间函数
        query = f"""
            SELECT 
                -- 7天前0点至今（使用Python计算的时间戳）
                SUM(CASE WHEN last_save_time >= {seven_days_ts} THEN 1 ELSE 0 END) AS `7天前至今`,
                -- 3天前0点至今（使用Python计算的时间戳）
                SUM(CASE WHEN last_save_time >= {three_days_ts} THEN 1 ELSE 0 END) AS `3天前至今`,
                -- 等级统计
                SUM(CASE WHEN `level` >= 10 THEN 1 ELSE 0 END) AS `10级`,
                SUM(CASE WHEN `level` >= 30 THEN 1 ELSE 0 END) AS `30级`,
                SUM(CASE WHEN `level` >= 80 THEN 1 ELSE 0 END) AS `80级`,
                SUM(CASE WHEN `level` >= 130 THEN 1 ELSE 0 END) AS `130级`
            FROM role
        """
        cursor.execute(query)
        counts = cursor.fetchone()

        if counts:
            result["7天前至今"], result["3天前至今"], result["10级"], result["30级"], result["80级"], result["130级"] = counts

        logging.debug(f"服务器 {server_id} 查询完成")

    except OperationalError:
        logging.warning(f"服务器 {server_id} 连接失败")
    except Exception as e:
        logging.error(f"服务器 {server_id} 处理错误: {e}")
    finally:
        if conn and conn.open:
            try:
                conn.close()
            except Exception:
                pass

    return result


def batch_query_and_save_excel():
    # 用Python计算时间阈值（所有服务器共用同一时间基准）
    seven_days_ts, three_days_ts = get_time_thresholds()
    logging.info(f"时间基准：7天前0点={datetime.fromtimestamp(seven_days_ts)}, 3天前0点={datetime.fromtimestamp(three_days_ts)}")

    # 基础配置
    host = "114.67.155.186"
    start_port = 20001
    end_port = 20100
    max_workers = 100  # 并发数
    output_file = "服务器数据统计.xlsx"

    logging.info(f"开始查询1-100服数据（端口{start_port}-{end_port}）...")

    # 生成服务器列表
    servers = [
        (server_id, host, start_port + server_id - 1)
        for server_id in range(1, 101)
    ]

    # 并发查询（传入Python计算的时间戳）
    all_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(query_server, sid, h, p, seven_days_ts, three_days_ts): sid
            for sid, h, p in servers
        }

        for future in as_completed(futures):
            sid = futures[future]
            try:
                result = future.result()
                all_results.append(result)
            except Exception as e:
                logging.error(f"服务器 {sid} 线程执行错误: {e}")
                all_results.append({
                    "服务器序号": sid,
                    "7天前至今": None,
                    "3天前至今": None,
                    "10级": None,
                    "30级": None,
                    "80级": None,
                    "130级": None,
                })

    # 按服务器序号排序
    all_results.sort(key=lambda x: x["服务器序号"])

    # 生成Excel
    try:
        df = pd.DataFrame(all_results)
        columns_order = [
            "服务器序号", "7天前至今", "3天前至今",
            "10级", "30级", "80级", "130级"
        ]
        df = df[columns_order]
        df.to_excel(output_file, index=False, engine="openpyxl")
        logging.info(f"所有数据已写入 {output_file}，共{len(all_results)}条记录")
    except Exception as e:
        logging.error(f"生成Excel失败: {e}")


def start_query():
    batch_query_and_save_excel()
    result_label.config(text="数据查询和保存完成！")


# 创建主窗口
root = tk.Tk()
root.title("服务器数据查询工具")
root.geometry("400x300")

# 创建标签
label = tk.Label(root, text="点击按钮开始查询服务器数据并保存到Excel")
label.pack(pady=20)

# 创建按钮
query_button = tk.Button(root, text="开始查询", command=start_query)
query_button.pack(pady=20)

# 创建用于显示结果的标签
result_label = tk.Label(root, text="")
result_label.pack(pady=20)

# 启动窗口的主循环
root.mainloop()