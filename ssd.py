from pymongo import MongoClient
from datetime import datetime, timedelta
import time


def count_users_by_zone_and_condition():
    # -------------------------- 1. 配置连接信息 --------------------------
    mongo_uri = "mongodb://localhost:27017/"  # MongoDB 连接地址（默认本地）
    db_name = "shanhaitbkf"  # 替换为你的数据库名
    collection_name = "user"  # 集合名（已确定为 user）

    # 分区字段（默认 data.sid，若需修改为 hdcid 则改为 "hdcid"，子文档字段需带引号如 "data.zone"）
    group_by_field = "data.sid"

    # -------------------------- 2. 定义统计条件 --------------------------
    # 等级阈值（≥10/40/70/100）
    level_thresholds = [10, 40, 70, 100]
    # 登录时间范围（3天内、7天内，转换为 Unix 时间戳（秒））
    current_ts = int(time.time())  # 当前时间戳
    time_conditions = {
        "3天内登录": current_ts - 3 * 24 * 3600,
        "7天内登录": current_ts - 7 * 24 * 3600
    }

    # -------------------------- 3. 连接 MongoDB --------------------------
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        print("MongoDB 连接成功！")
    except Exception as e:
        print(f"MongoDB 连接失败：{str(e)}")
        return

    # -------------------------- 4. 执行统计（循环所有条件） --------------------------
    print("\n" + "=" * 80)
    print(f"按分区（{group_by_field}）统计结果")
    print("=" * 80)

    # 统计1：各等级阈值（≥N级）的用户数
    for level in level_thresholds:
        pipeline = [
            # 筛选：等级≥当前阈值
            {"$match": {"data.level": {"$gte": level}}},
            # 按分区分组统计
            {"$group": {"_id": f"${group_by_field}", "用户数": {"$sum": 1}}},
            # 按分区ID排序
            {"$sort": {"_id": 1}}
        ]

        result = list(collection.aggregate(pipeline))
        print(f"\n【等级≥{level}级】")
        if result:
            for item in result:
                print(f"  分区{item['_id']}：{item['用户数']}人")
        else:
            print("  无符合条件的用户")

    # 统计2：各登录时间范围的用户数（不限等级，若需叠加等级条件可修改 $match）
    for time_name, min_ts in time_conditions.items():
        pipeline = [
            # 筛选：最后登录时间≥最小时间戳（即在时间范围内）
            {"$match": {"data.lastlogin": {"$gte": min_ts}}},
            # 按分区分组统计
            {"$group": {"_id": f"${group_by_field}", "用户数": {"$sum": 1}}},
            # 按分区ID排序
            {"$sort": {"_id": 1}}
        ]

        result = list(collection.aggregate(pipeline))
        print(f"\n【{time_name}】")
        if result:
            for item in result:
                print(f"  分区{item['_id']}：{item['用户数']}人")
        else:
            print("  无符合条件的用户")

    # -------------------------- 5. 可选：统计“等级+登录时间”叠加条件 --------------------------
    print("\n" + "-" * 80)
    print("可选：等级≥10级 + 7天内登录（叠加条件示例）")
    print("-" * 80)
    pipeline = [
        {"$match": {
            "data.level": {"$gte": 10},
            "data.lastlogin": {"$gte": time_conditions["7天内登录"]}
        }},
        {"$group": {"_id": f"${group_by_field}", "用户数": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        for item in result:
            print(f"  分区{item['_id']}：{item['用户数']}人")
    else:
        print("  无符合条件的用户")

    client.close()


if __name__ == "__main__":
    count_users_by_zone_and_condition()