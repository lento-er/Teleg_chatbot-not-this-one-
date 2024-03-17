# telegram_chatgpt_bot
## 自行部署服务使用说明
1. 自行部署，使用use_config目录下的代码
2. 安装依赖库，在终端执行命令【pip install requirements.txt】
3. 在终端执行命令【python main.py】，此时服务启动
4. 在telegram上同机器人对话即可看到效果
5. telegram及chatgpt相关配置在config.ini文件中，视情况自行修改

## 在fly.io上启动服务使用说明
1. 相关配置已经在fly.io上填写，因此根目录下的代码未使用config.ini文件，若需修改token等信息，请至fly.io上处理
2. 登录fly.io，进入Dashboard
3. 选择左侧的Machines
4. 点击服务【3287ee1f750485】右侧的启动
5. 在telegram上同机器人对话即可看到效果
6. 每次push代码时，会自动重新部署并启动fly.io上的服务