# CKB Node
# Mainnet: https://public-service-status-checker-magickbase.vercel.app/api/ckb/node/mainnet
# Testnet: https://public-service-status-checker-magickbase.vercel.app/api/ckb/node/testnet
# CKB Explorer

# Mainnet: https://public-service-status-checker-magickbase.vercel.app/api/ckb/explorer/mainnet
# Testnet: https://public-service-status-checker-magickbase.vercel.app/api/ckb/explorer/testnet
# Godwoken Explorer

# Mainnet: https://public-service-status-checker-magickbase.vercel.app/api/gw/explorer/mainnet
# Testnet: https://public-service-status-checker-magickbase.vercel.app/api/gw/explorer/testnet
# Faucet

# Testnet: https://public-service-status-checker-magickbase.vercel.app/api/ckb/faucet

from flask import Flask, render_template, request, jsonify,json
import datetime
import threading
import requests
import datetime
# import pytz
# from apscheduler.schedulers.background import BackgroundScheduler
import requests
import threading
import re
services = [
    {"name": "CKB 主网节点","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/node/mainnet"},
    {"name": "CKB 测试网节点","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/node/testnet"},
    {"name": "CKB 主网浏览器","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/explorer/mainnet"},
    {"name": "CKB 测试网浏览器","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/explorer/testnet"},
    {"name": "Godwoken 主网浏览器","url":"https://public-service-status-checker-magickbase.vercel.app/api/gw/explorer/mainnet"},
    {"name": "Godwoken 测试网浏览器","url":"https://public-service-status-checker-magickbase.vercel.app/api/gw/explorer/testnet"},
    {"name": "CKB 水龙头","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/faucet"},
]


app = Flask(__name__)

def iso8601(time_str):
    # 解析 ISO 8601 时间字符串
    time = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    # 将时间转换为中国时间
    china_tz = pytz.timezone('Asia/Shanghai')
    china_time = time.replace(tzinfo=pytz.utc).astimezone(china_tz)
    # 输出结果
    return(china_time.strftime("%Y-%m-%d %H:%M:%S %Z%z"))

def timestamp_to_china_time(timestamp):
    # 将 Unix 时间戳转换为 Python 的 datetime 对象
    time = datetime.datetime.fromtimestamp(timestamp / 1000)

    # 将时间转换为中国时间
    china_tz = pytz.timezone('Asia/Shanghai')
    china_time = time.replace(tzinfo=pytz.utc).astimezone(china_tz)

    # 返回中国时间的字符串表示
    return china_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")

# 返回 HTML 页面
@app.route('/')
def index():                
    return render_template('index.html')

# # 返回 JSON 数据
@app.route('/api')
def api():
    data = {"name": "John", "age": 30}
    data2 = []
    data3 = {}
    check_info = [
        {"name": "CKB Faucet","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/faucet"},
        {"name": "CKB Node Mainnet","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/node/mainnet"},
        {"name": "CKB Explorer Mainnet","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/explorer/mainnet"},
        {"name": "CKB Node Testnet","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/node/testnet"},
        {"name": "CKB Explorer Testnet","url":"https://public-service-status-checker-magickbase.vercel.app/api/ckb/explorer/testnet"},
        {"name": "Godwoken Explorer Mainnet ","url":"https://public-service-status-checker-magickbase.vercel.app/api/gw/explorer/mainnet"},
        {"name": "Godwoken Explorer Testnet","url":"https://public-service-status-checker-magickbase.vercel.app/api/gw/explorer/testnet"},
    ]
    for i in check_info:
        try:
            r = requests.get(url=i["url"], timeout=10)
            data = json.loads(r.text) 
            print(i['name'],data)   
            # 判断是浏览器还是节点：
            if "header" in data: # 区块节点
                #print(data, i['name'])
                #print(i['name'], timestamp_to_china_time(data["header"]['timestamp']))
                data2.append({i['name']: data['header']['number']})
            elif "block" in r.text: # 浏览器
                
                # print( i['name'], iso8601(data['block']['timestamp']))
                data2.append({i['name']: data['block']['number']})
            elif "claim" in r.text: # 水龙头
                data2.append({i['name']: data['claim']['status']})
                # data2.append(data)
        except Exception as e:
             data2.append({i['name']: str(e)})
             
    try:
        # k8s interal gw
        print("k8s")
        response = requests.get(url="http://testnet-gw-readonly.testnet:8119" + '/metrics')
        # 使用正则表达式从指标数据中过滤出 gw_chain_block_height 的值
        pattern = r'^gw_chain_block_height\s+(\d+)$'
        match = re.search(pattern, response.text, re.MULTILINE)
        if match:
            block_height = int(match.group(1))
            data2.append({"Godwoken Testnet Node": block_height})

        response = requests.get(url="http://gw-readonly.mainnet:8119" + '/metrics')
        # 使用正则表达式从指标数据中过滤出 gw_chain_block_height 的值
        pattern = r'^gw_chain_block_height\s+(\d+)$'
        match = re.search(pattern, response.text, re.MULTILINE)
        if match:
            block_height = int(match.group(1))
            data2.append({"Godwoken Mainnet Node": block_height})
    except Exception as e:
        print(e)
    return data2

                            

def check_services():
    for service in services:
        url = service["url"]
        name = service["name"]
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"{name} is down with status code {response.status_code}")
            else:
               print(f"{name} is ok {response.status_code}")     
               alert(name)
        except Exception as e:
            alert(name)

def alert(name):
    # 在这里实现告警逻辑，可以通过邮件或短信等方式发送告警信息
    data = '''
            {
                "msg_type": "interactive", 
                "card": {
                    "elements": [
                    
                        {
                            "tag": "div", 
                            "text": {
                                "content": "", 
                                "tag": "lark_md"
                            }
                        }, 
                        {
                            "elements": [
                                {
                                    "content": "✅ Mike handled this alert.", 
                                    "tag": "plain_text"
                                }
                            ], 
                            "tag": "note"
                        }
                    ], 
                    "header": {
                        "template": "red", 
                        "title": {
                            "content": "告警恢复", 
                            "tag": "plain_text"
                        }
                    }
                }
            }
    '''
    r = requests.post(url="https://open.larksuite.com/open-apis/bot/v2/hook/3ac6969f-beac-4674-83bb-bd03759480d3", data=json.dumps(data))
    print(r.content)

    

if __name__ == '__main__':
    # 启动定时任务的线程
    # scheduler_thread = threading.Thread(target=start_scheduler)
    # scheduler_thread.start()
                             
    
    # 启动 Flask 应用程序
    app.run(debug=True, host="0.0.0.0")