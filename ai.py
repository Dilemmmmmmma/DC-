import requests
import json
import random
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# 获取指定频道的名称
def get_channel_name(auth, channel_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}"
    headers = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            channel_info = res.json()
            channel_name = channel_info.get("name", "未知频道")
            logging.info(f"频道 {channel_id} 的名称是: {channel_name}")
            return channel_name
        else:
            logging.error(f"获取频道 {channel_id} 名称失败，状态码: {res.status_code}")
            return f"获取频道名称失败，状态码: {res.status_code}"
    except requests.exceptions.RequestException as e:
        logging.error(f"请求频道 {channel_id} 名称时发生错误: {e}")
        return f"请求错误: {e}"

        

# 获取指定频道的历史消息内容
def get_context(auth, chanel_id):
    header = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }
    url = f"https://discord.com/api/v10/channels/{chanel_id}/messages?limit=10"
    try:
        res = requests.get(url=url, headers=header)
        if res.status_code == 200:
            result = json.loads(res.content)
            result_list = []
            for context in result:
                if ('<') not in context['content']:
                    if ('@') not in context['content']:
                        if ('http') not in context['content']:
                            if ('?') not in context['content']:
                                result_list.append(context['content'])
            if result_list:

                return result_list
            else:
                logging.info("没有找到有效的消息。")
                
        else:
            logging.error(f"获取消息失败，状态码: {res.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"请求错误: {e}")
        

# 向GPT-4o mini模型发送请求并生成响应
def generate_response(messages):
    gpt_api_url = "https://geekai.dev/api/v1/chat/completions"  # 更新为示例中的URL
    headers = {
        "Authorization": "Bearer 用你的API Key替换这里",  # 用你的API Key替换这里
        "Content-Type": "application/json"
    }

    # 创建一个prompt，包含你想要的描述
    prompt = f"我需要生成一个简短的回答，基于以下聊天内容。我是一个Web3的从业者，请在聊天内容的上下文基础上做出幽默而简短的回应，10字以内，不要标点符号，间隔用空格代替。消息内容：{messages}" #你也可以自定义prompt

    payload = {
        "model": "gpt-4o-mini",  # 请根据你的实际模型调整
        "messages": [{"role": "user", "content": prompt}],
        "stream": False  # 示例请求中包含了stream参数
    }

    try:
        # 使用 POST 请求发送数据
        response = requests.post(gpt_api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            gpt_response = response.json()
            # 假设返回的响应格式与示例相同
            return gpt_response['choices'][0]['message']['content'].strip()
        else:
            logging.error(f"GPT-4o mini API 请求失败，状态码: {response.status_code}")
            return "生成消息失败"
    except requests.exceptions.RequestException as e:
        logging.error(f"请求 GPT-4o mini 时发生错误: {e}")
        return "请求失败"

# 发送消息到指定的 Discord 频道
def chat(chanel_list, authorization):
    header = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }

    for channel_id in chanel_list:
        try:
            channel_name = get_channel_name(authorization, channel_id)  # 获取频道名称
            messages = get_context(authorization, channel_id)  # 获取消息内容
            if messages and messages != ["获取消息失败"]:
                messages_text = " ".join(messages)  # 将消息内容连接成一个字符串

                # 调用 GPT-4o mini 生成简短的回答
                gpt_response = generate_response(messages_text)

                # 构造消息内容
                msg = {
                    "content": gpt_response,
                    "nonce": f"82329451214{random.randrange(0, 1000)}33232234",  # 为每条消息生成唯一标识符
                    "tts": False,  # 设置是否为语音消息
                }
                url = f"https://discord.com/api/v10/channels/{channel_id}/messages"  # 构建消息发送的 URL
                # 发送 POST 请求，将消息发送到 Discord 频道
                res = requests.post(url=url, headers=header, data=json.dumps(msg))

                if res.status_code in [200, 201]:
                    logging.info(f"Token {authorization[:6]}...成功向频道 {channel_name} 发送消息: {msg['content'][:50]}...")
                else:
                    logging.error(f"Token {authorization[:6]}...向频道 {channel_name} 发送消息失败，状态码: {res.status_code}, 响应: {json.dumps(res.json(), ensure_ascii=False)}")

                # 程序休眠指定的时间
                sleeptime = random.randrange(100, 300)  # 设置发送间隔时间，随机选择 100 到 300 秒之间
                logging.info(f"程序将休眠 {sleeptime} 秒")
                time.sleep(sleeptime)

        except Exception as e:
            logging.error(f"Token {authorization[:6]}...向频道 {channel_id} 发送消息时出错: {e}")

# 主程序入口
if __name__ == "__main__":
    chanel_list = ["12345678912345789456"]  # 这里是 Discord 频道的 ID
    authorization_list = "OTc1Mhjkjkhlkjhkljhjkhlhhjkhkjhjk"  # 这里是 Bot 的授权令牌（Token）

    while True:
        try:
            # 获取指定频道的所有有效消息
            messages = get_context(authorization_list, chanel_list[0])
            logging.info(f"获取的消息: {messages}")  # 打印所有符合条件的消息

            if messages and messages != ["获取消息失败"]:
                # 处理完消息后才进行休眠
                chat(chanel_list, authorization_list)  # 调用发送消息的函数
            else:
                logging.info("没有获取到有效的消息，继续重试...")
        except Exception as e:
            logging.error(f"主循环发生错误: {e}")
            continue  # 继续执行下一个循环
