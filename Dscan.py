import requests
import threading
import queue
import time
import argparse

#输出banner信息
print(
'\033[1;34m(  __  \ (  ____ \(  ____ \(  ___  )( (    /|     /  \     (  __   )\033[0m\n'
'\033[1;34m| (  \  )| (    \/| (    \/| (   ) ||  \  ( |     \/) )    | (  )  |\033[0m\n'
'\033[1;34m| |   ) || (_____ | |      | (___) ||   \ | | _____ | |    | | /   |\033[0m\n'
'\033[1;34m| |   | |(_____  )| |      |  ___  || (\ \) |(_____)| |    | (/ /) |\033[0m\n'
'\033[1;34m| |   ) |      ) || |      | (   ) || | \   |       | |    |   / | |\033[0m\n'
'\033[1;34m| (__/  )/\____) || (____/\| )   ( || )  \  |     __) (_ _ |  (__) |\033[0m\n'
'\033[1;34m(______/ \_______)(_______/|/     \||/    )_)     \____/(_)(_______)\033[0m\n'
'\033[1;34m                                                                    \033[0m\n')


# 创建命令行参数解析器
parser = argparse.ArgumentParser(description="A multi-threaded sensitive directory scanner.")
parser.add_argument("-u", "--url", required=True, help="Target URL.")
parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file.")
parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads.")
parser.add_argument("-d", "--delay", type=float, default=0, help="Delay between each request.")
args = parser.parse_args()

# 获取命令行参数
url = args.url.rstrip("/") 
wordlist_path = args.wordlist
num_threads = args.threads
delay = args.delay

# 读取字典文件并保存到列表中
with open(wordlist_path, "r+") as f:
    wordlist = [line.strip() for line in f]

# 创建队列保存待扫描的路径
paths = queue.Queue()
for word in wordlist:
    paths.put(word)

# 声明一个集合来保存已经输出过的结果
visited = set()

# 发送 HTTP 请求并判断状态码
def scan_path(path):
    try:
        response = requests.get(url + path)
        if response.status_code in [200, 500]:
            # 如果结果不在集合中，则输出并将其加入集合
            result = f"{url}{path} ({response.status_code})"
            if result not in visited:
                visited.add(result)
                print(result)
    except requests.exceptions.RequestException:
        pass

# 多线程扫描
def worker():
    while True:
        path = paths.get()
        scan_path(path)
        paths.task_done()
        time.sleep(delay)

# 创建并启动多个线程
for i in range(num_threads):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

# 等待所有任务完成
paths.join()

