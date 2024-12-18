import requests
import json
import random
import time
import threading
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def get_context(auth, channel_id):
    headers = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=100"
    
    logging.info(f"请求频道 {channel_id} 的消息")
    
    try:
        res = requests.get(url=url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            result = res.json()
            result_list = [
                context['content'] for context in result
                if all(char not in context['content'] for char in ['<', '@', 'http', '?'])
            ]
            if result_list:
                selected_msg = random.choice(result_list)
                logging.info(f"成功获取消息：{selected_msg[:50]}...")
                return selected_msg
            else:
                logging.warning(f"频道 {channel_id} 没有找到有效的消息")
                return "没有有效的消息"
        else:
            logging.error(f"获取频道 {channel_id} 消息失败，状态码: {res.status_code}, 响应: {json.dumps(res.json(), ensure_ascii=False)}")
            return f"获取消息失败 - {res.status_code}"
    except requests.exceptions.RequestException as e:
        logging.error(f"请求频道 {channel_id} 消息时发生错误: {e}")
        return ""

def chat(channel_id, authorization, token_index):
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }
    
    try:
        msg_content = get_context(authorization, channel_id)
        msg = {
            "content": msg_content,
            "nonce": f"82329451214{random.randrange(0, 1000)}33232234",
            "tts": False,
        }
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        
        res = requests.post(url=url, headers=headers, data=json.dumps(msg), timeout=10)
        
        if res.status_code in [200, 201]:
            logging.info(f"Token {token_index+1}/15 ({authorization[:6]}...) 成功向频道 {channel_id} 发送消息: {msg_content[:50]}...")
        else:
            logging.error(f"获取频道 {channel_id} 消息失败，状态码: {res.status_code}, 响应: {json.dumps(res.json(), ensure_ascii=False)}")
    except Exception as e:
        logging.error(f"向频道 {channel_id} 发送消息时出错: {e}")

def chat_thread(channel_id, tokens, start_hour, end_hour):
    while True:
        now = datetime.now()
        
        if start_hour <= now.hour < end_hour:
            # 使用线程池并发处理 tokens
            with ThreadPoolExecutor(max_workers=len(tokens)) as executor:
                futures = []
                for i, token in enumerate(tokens):
                    # 为每个 token 生成一个随机发送时间
                    random_delay = random.uniform(1200, 7200)  # 随机延迟，最多1小时
                    # 记录 token 的等待时长
                    logging.info(f"Token {i+1} 将等待 {random_delay:.2f} 秒后向 {channel_id}发送消息")
                    future = executor.submit(
                        delayed_chat, 
                        channel_id, 
                        token, 
                        i, 
                        random_delay
                    )
                    futures.append(future)
                
                # 等待所有任务完成
                for future in futures:
                    future.result()
                
                # 在所有 token 发送完毕后，等待较长时间
                time.sleep(random.randint(43200, 64800))
        else:
            # 如果不在时间范围内，计算下一个开始时间
            next_start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            if now.hour >= end_hour:
                next_start_time += timedelta(days=1)
            
            wait_time = (next_start_time - now).total_seconds()
            logging.info(f"频道 {channel_id} 当前不在时间段内，将在 {next_start_time} 开始发送消息，等待 {wait_time} 秒")
            time.sleep(wait_time)

def send_message_with_delay(channel_id, token, delay=None):
    # 如果没有传入延迟，则使用随机延迟
    if delay is None:
        delay = random.uniform(300, 900)
    time.sleep(delay)  # 延迟
    send_message(channel_id, token)  # 发送消息

def delayed_chat(channel_id, token, token_index, delay):
    send_message_with_delay(channel_id, token, delay)  # 统一使用延迟处理

if __name__ == "__main__":
    intervals = {
        "123456789987123456": (3, 23),    # 活跃时间为 03:00 到 23:00
        "1234565478942312235": (12, 23),  # 活跃时间为 12:00 到 23:00
    }

    authorization_list = [
        "OTc……",
        "OTc……",
        "OTc……"
    ]

    threads = []
    for channel_id, (start_hour, end_hour) in intervals.items():
        thread = threading.Thread(
            target=chat_thread, 
            args=(channel_id, authorization_list, start_hour, end_hour),
            name=f"Thread-{channel_id}"
        )
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("收到键盘中断，正在关闭线程...")
        for thread in threads:
            thread.join(timeout=5)
        logging.info("所有线程已关闭")
