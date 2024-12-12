import requests
import json
import random
import time
import threading
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("discord_bot.log", encoding='utf-8'),
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
            logging.error(f"获取频道 {channel_id} 消息失败，状态码: {res.status_code}, 响应: {res.text}")
            return f"获取消息失败 - {res.status_code}"
    except requests.exceptions.RequestException as e:
        logging.error(f"请求频道 {channel_id} 消息时发生错误: {e}")
        return "请求失败"

def chat(channel_id, authorization):
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
            logging.info(f"Token {authorization[:6]}... 成功向频道 {channel_id} 发送消息: {msg_content[:50]}...")
        else:
            logging.error(f"向频道 {channel_id} 发送消息失败，状态码: {res.status_code}, 响应: {res.text}")
    except Exception as e:
        logging.error(f"向频道 {channel_id} 发送消息时出错: {e}")

def get_random_time_in_range(start_hour, end_hour):
    if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23 and start_hour <= end_hour):
        logging.error(f"无效的时间范围: {start_hour} 到 {end_hour}")
        return None

    start_time = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    random_minutes = random.randint(0, int((end_time - start_time).total_seconds() // 60))
    random_time = start_time + timedelta(minutes=random_minutes)
    return random_time

def chat_thread(channel_ids, all_tokens, start_hour, end_hour):
    error_count = 0
    max_errors = 5
    
    while True:
        try:
            now = datetime.now()
            if start_hour <= now.hour < end_hour:
                for channel_id in channel_ids:
                    selected_token = random.choice(all_tokens)
                    random_time = get_random_time_in_range(now.hour, end_hour)
                    
                    if random_time is None:
                        continue
                    
                    time_to_wait = max(0, (random_time - now).total_seconds())
                    logging.info(f"频道 {channel_id} 将在 {random_time} 发送消息，等待 {time_to_wait} 秒")
                    
                    time.sleep(time_to_wait)
                    chat(channel_id, selected_token)
                    
                    time.sleep(random.randint(900, 1800))
            else:
                next_start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
                if now >= next_start_time:
                    next_start_time += timedelta(days=1)
                time_to_wait = (next_start_time - now).total_seconds()
                logging.info(f"当前不在时间段内，将在 {next_start_time} 开始发送消息，等待 {time_to_wait} 秒")
                time.sleep(time_to_wait)
        except Exception as e:
            error_count += 1
            logging.error(f"发生错误（{error_count}/{max_errors}）: {e}")
            time.sleep(5 * error_count)
        
        if error_count >= max_errors:
            logging.critical(f"线程因连续错误超过{max_errors}次而退出")
            break

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
            args=([channel_id], authorization_list, start_hour, end_hour),
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