import requests
import logging
import os

class HKBU_ChatGPT():

    def submit(self, message):
        logging.info(f'用户发过来的消息是:{message}')
        url = (os.environ['CHATGPTBASICURL']) + "/deployments/" + (
        os.environ['CHATGPTMODELNAME']) + "/chat/completions/?api-version=" + (
              os.environ['CHATGPTAPIVERSION'])
        headers = {'Content-Type': 'application/json', 'api-key': (os.environ['CHATGPTACCESS_TOKEN'])}
        payload = {'messages': message}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            logging.info(f'chatgpt回复的消息是:{data}')
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response


if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()

    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)
