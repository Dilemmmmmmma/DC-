# Discord 聊天机器人多号版

此机器人用于在指定时间向多个 Discord 频道发送消息。它从指定频道获取消息，过滤后选择一条消息并发送回去。该机器人基于 Discord API 和 Python 的线程模块实现多频道并发操作。
![Proof](https://i.ibb.co/vQkwwmb/We-Chat-20241212200238.jpg)

## 功能特点
- 自动从指定的 Discord 频道获取最近100条消息。
- 将选取的消息发送回相同或其他指定的频道。
- 支持从过滤后的内容中随机选择消息。
- 为每个频道设定特定的活跃时间段。
- 全面的日志记录功能，用于调试和监控。
- 支持多个token
- 支持多个频道
- 95%的代码来自Chatgpt和Claude


## 需要的工具

- 手
- Python 版本 3.10 或更高。


## 安装方法

1. 克隆代码库：
    ```bash
    git clone https://github.com/Dilemmmmmmma/DC-Chat-bots
    ```

2. 安装所需的 Python 包：
    ```bash
    pip install -r requirements.txt
    ```

3. 根据需要更新脚本中的 `authorization_list` 和 `intervals` 变量，填入您的 Discord 机器人令牌和频道的活跃时间段。

4. 运行机器人：
    ```bash
    python main.py
    ```

## 配置说明

### `authorization_list`
- 包含 Discord 机器人令牌的列表，用于身份验证。
- 确保每个令牌均有效，并对指定频道具有足够的权限。
- 示例：
    ```python
    authorization_list = [
        "OTc1……",
        "OTc1……",
        "OTc……"
    ]
    ```


### `intervals`
- 一个字典，映射频道 ID 到其活跃的时间范围。
- 示例：
    ```python
    intervals = {
        "123456789987123456": (3, 23),  # 活跃时间为 03:00 到 23:00
        "1234565478942312235": (12, 23)  # 活跃时间为 12:00 到 23:00
    }
    ```

### 日志
- 日志存储在 `discord_bot.log` 文件中，同时也会输出到控制台。
- 日志格式包含时间戳、日志级别和消息内容。

## 核心函数

### `get_context(auth, channel_id)`
- 获取指定频道最近的 100 条消息。
- 过滤掉包含 `<`, `@`, `http`, 或 `?` 的消息。
- 随机选择一条有效消息返回。

### `chat(channel_id, authorization)`
- 使用指定的令牌向指定频道发送选定的消息。

### `get_random_time_in_range(start_hour, end_hour)`
- 在指定时间范围内生成一个随机时间。

### `chat_thread(channel_ids, all_tokens, start_hour, end_hour)`
- 在指定的活跃时间范围内，为多个频道处理消息发送。

## 注意事项
- 如果连续出现超过配置阈值（`max_errors`）的错误，机器人将停止运行。
- 遵守 Discord API 的限流规则，过多请求可能导致临时封禁。
