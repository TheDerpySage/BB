# https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=0
client_id = 0
token = ""
server_id = 0
general_chat_id = 0
reporting_chat_id = 0
log_chat_id = 0
owner_id = 0
super_role = ""
mod_role = ""
# REPORTING
reporting = False
serverList = []
serviceList = []
checkInterval = 120
retryInterval = 5
# EMAILER
send_alerts_to = ''
host = ''
username = ''
password = ''
# VIRUSTOTAL
vt_api_key = ''
# OPENAI
openai_key = ""
openai_name = ""
davinci_personality = "I am" + openai_name + "\n\n"
turbo_personality = "You are" + openai_name + ""
openai_auto_chance = 0.05
# OTHER
CONNECTED = False