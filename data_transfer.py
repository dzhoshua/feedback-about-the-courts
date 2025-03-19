import requests
import json

def send_data(message) -> None:
    # Вставить свои куки
    cookies = {
        'kc-access':'',
        'kc-state':'YOUR DATA'
        }
    
    # В зависимости от браузера поменять параметры 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'tz-offset': '28800',
        'x-trace-id': '54b873bc57d34fe49aee68123f8f5692',
        'Origin': 'https://test.core.talisman.ispras.ru',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    json_data = {
        'operationName': 'createPipelineTopicMessage',
        'variables': {
            'message':f"{message}",
            'priority': 'Normal',
            'topic':'sud-test-proc'
        },
        'extensions': {},
        'query':'mutation createPipelineTopicMessage($topic: String!, $priority: MessagePriority!, $message: JSON!) {\n createPipelineTopicMessage: addMessage(\n topic: $topic\n priority: $priority\n message: $message\n ) {\n id\n __typename\n }\n }'
        }

    return requests.post('https://test.core.talisman.ispras.ru/graphql', cookies=cookies, headers=headers,
                         json=json_data)


with open("./!items.json", "r") as f:
    data = json.load(f)
         
    for line in data:
        string = f"{line}"
        new_line = ""
        for char in string:
            # print(char)
            if char == "'":
                new_line += '\"'
            else:
                new_line += char
        # print(new_line)
        res = send_data(new_line)
        print(res)
        
        