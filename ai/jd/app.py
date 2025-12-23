from flask import Flask, render_template, request, Response, jsonify
import requests
import json
import time
import logging
import os

# 配置日志
logging.basicConfig(level=logging.DEBUG)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# 初始化Flask应用
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config['JSON_AS_ASCII'] = False


# 跨域支持
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# 配置项（替换为你的有效API Key）
API_KEY = "pk-6290db4e-5df0-46ea-9452-e42e6a44e325"
JD_CLOUD_API_URL = "http://ai-api.jdcloud.com/v1/chat/completions"


def generate_ai_response(messages):
    """流式调用京东云AI API，包含去重逻辑"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept": "text/event-stream",
    }

    payload = {
        "stream": True,
        "model": "gpt-5",
        "messages": messages
    }

    start_time = time.time()
    response = None
    last_content = ""  # 记录上一次推送的内容，用于去重

    try:
        response = requests.post(
            url=JD_CLOUD_API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=(10, 120),
            allow_redirects=False,
        )
        response.raise_for_status()

        for line in response.iter_lines(chunk_size=1024, decode_unicode=False):
            # 超时检查
            if time.time() - start_time > 120:
                yield f"data: {json.dumps({'type': 'error', 'content': '请求超时（已超过120秒）'})}\n\n"
                break

            if not line:
                continue

            # 解析响应行
            line_str = line.decode("utf-8", errors="ignore").strip()
            if line_str.startswith("data: "):
                line_data = line_str.split("data: ", 1)[1].strip()

                # 处理结束标识
                if line_data == "[DONE]":
                    yield f"data: {json.dumps({'type': 'end'})}\n\n"
                    break

                # 解析JSON并去重推送
                try:
                    json_data = json.loads(line_data)
                    if "choices" in json_data:
                        for choice in json_data["choices"]:
                            content = choice.get("delta", {}).get("content", "")
                            # 去重：只推送非空且不重复的内容
                            if content and content != last_content:
                                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                                last_content = content
                except json.JSONDecodeError:
                    continue

    except requests.exceptions.ConnectTimeout:
        yield f"data: {json.dumps({'type': 'error', 'content': '连接超时：无法连接到API服务器'})}\n\n"
    except requests.exceptions.ReadTimeout:
        yield f"data: {json.dumps({'type': 'error', 'content': '读取超时：服务器响应过慢'})}\n\n"
    except requests.exceptions.RequestException as e:
        err_msg = f"API请求失败：{str(e)}"
        if response:
            err_msg += f" | 状态码：{response.status_code}"
        yield f"data: {json.dumps({'type': 'error', 'content': err_msg})}\n\n"
    finally:
        if response:
            response.close()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/translate', methods=['POST', 'OPTIONS'])
def translate_code():
    """代码翻译接口（流式）"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体必须为JSON格式"}), 400

        code = data.get("code", "").strip()
        from_lang = data.get("from_lang", "java")
        to_lang = data.get("to_lang", "python")

        if not code:
            return jsonify({"error": "代码内容不能为空"}), 400

        # 构造翻译提示词
        prompt = f"""请将以下{from_lang}代码翻译成{to_lang}代码，保持功能一致，不添加额外解释：

{code}
"""

        # 构造消息列表
        messages = [{"role": "user", "content": prompt}]

        # 返回流式响应
        return Response(
            generate_ai_response(messages),
            mimetype='text/event-stream'
        )
    except Exception as e:
        logging.error(f"Translate接口异常：{str(e)}", exc_info=True)
        return jsonify({"error": f"服务器内部错误：{str(e)}"}), 500


if __name__ == '__main__':
    # 启动服务（生产环境请关闭debug，移除use_reloader）
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)