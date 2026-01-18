from flask import Flask, render_template, request, jsonify
import requests
import json
import time
import logging
import os

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 配置项（替换为你的有效API Key）
API_KEY = "pk-6290db4e-5df0-46ea-9452-e42e6a44e325"
JD_CLOUD_API_URL = "http://ai-api.jdcloud.com/v1/chat/completions"

def call_ai_service(log_content):
    """调用京东云AI API进行日志分析"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 构造 Prompt，强制要求 JSON 格式
    prompt = f"""请扮演一个资深的系统运维和开发专家。请分析以下日志内容，并严格按照 JSON 格式返回分析结果。
请不要输出任何 Markdown 标记（如 ```json），只返回纯 JSON 字符串。

JSON 返回值结构必须满足以下 Schema：
{{
    "line_count": int, // 日志总行数（估算即可）
    "error_count": int, // 发现的错误数量
    "warning_count": int, // 发现的警告数量
    "errors": [ // 关键错误列表
        {{
            "type": "错误类型简述",
            "message": "错误的关键日志片段",
            "explanation": "通俗易懂的错误原因解释"
        }}
    ],
    "solutions": [ // 解决方案列表
        {{
            "error_type": "对应的错误类型",
            "suggestion": "核心修复建议",
            "steps": ["详细步骤1", "详细步骤2", "详细步骤3"]
        }}
    ]
}}

待分析日志内容：
{log_content[:10000]} 
""" 
    # 注意：截取前10000字符防止token溢出

    payload = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False, # 这里我们使用非流式，方便一次性解析 JSON
    }

    try:
        response = requests.post(
            url=JD_CLOUD_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            # 尝试清理可能的 markdown 标记
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
            
    except Exception as e:
        logging.error(f"AI 分析失败: {str(e)}")
        # 降级处理：返回一个包含错误信息的默认结构
        return {
            "line_count": len(log_content.split('\n')),
            "error_count": 1,
            "warning_count": 0,
            "errors": [{"type": "AI Analysis Failed", "message": str(e), "explanation": "AI 服务调用失败，请检查网络或日志内容。"}],
            "solutions": []
        }
    
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_log():
    data = request.json
    log_content = data.get('log', '')
    
    if not log_content:
        return jsonify({"error": "Empty log content"}), 400

    # 调用 AI 进行分析
    ai_result = call_ai_service(log_content)
    
    if ai_result:
        # 确保 line_count 准确（可选，AI 可能会估算错）
        ai_result['line_count'] = len(log_content.split('\n'))
        return jsonify(ai_result)
    else:
        return jsonify({"error": "Failed to analyze log"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)