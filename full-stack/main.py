
import os
import random
from telegram import Update, ReplyKeyboardMarkup  # Ensure python-telegram-bot package is installed and updated (>=20.0)
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, ContextTypes, filters

TOKEN = "7945188969:AAGqv31lZK0YaRjVTDqBXgTiCJyt1hyICnc"  # Replace with your token!

# Create the main ቁጥር directory and subdirectories for each day
os.makedirs("ቁጥር", exist_ok=True)
weekdays = ["ዘዘወትር","ሰኑይ", "ሠሉስ", "ረቡዕ", "ሐሙስ", "አርብ", "ቀዳሚት-ሰንበት", "ሰንበተ-ከርስቲያን-ቅድስት"]
for day in weekdays:
    os.makedirs(os.path.join("ቁጥር", day), exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["ዜማ","ቁጥር"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)


async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "ቁጥር":
        # Display the days for which files are saved
        keyboard = [["Main Menu"]]
        for day in weekdays:
            keyboard.append([day])  # Add each day as a button
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Select a day to view files:", reply_markup=reply_markup)
    elif text in weekdays:
        # Store the selected day
        context.user_data['selected_day'] = text
        # Display files for the selected day
        day_path = os.path.join("ቁጥር", text)
        files = os.listdir(day_path) if os.path.exists(day_path) else []
        keyboard = [["Main Menu"]]
        for file in files:
            keyboard.append([file])  # Add each file as a button
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"Files in {text}:", reply_markup=reply_markup)
    elif 'selected_day' in context.user_data and text in os.listdir(os.path.join("ቁጥር", context.user_data['selected_day'])):
        # Send the selected file
        file_path = os.path.join("ቁጥር", context.user_data['selected_day'], text)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, "rb"))
    elif text == "Main Menu":
        await start(update, context)
    else:
        await update.message.reply_text("Invalid option. Please use the buttons.")
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'selected_day' not in context.user_data:
        await update.message.reply_text("Please select a day to upload files first.")
        return

    file = update.message.document or update.message.photo[-1]
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else f"{random.randint(0, 200)}.jpg"
    selected_day = context.user_data['selected_day']

    new_file = await context.bot.get_file(file_id)
    file_path = os.path.join("ቁጥር", selected_day, file_name)

    await new_file.download_to_drive(file_path)
    await update.message.reply_text(f"File saved in '{selected_day}' folder as: {file_name}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_buttons))

    print("Bot is running...")
    app.run_polling()
# # Start command
# import os
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
# from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ApplicationBuilder, ContextTypes, filters
#
# TOKEN = "7945188969:AAGqv31lZK0YaRjVTDqBXgTiCJyt1hyICnc"  # Replace with your token!
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [["Add File", "Saved Files"]]
#     reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
#     await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
#
#
# async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = update.message.text
#
#     if text == "Add File":
#         await update.message.reply_text("Please send the file you want to upload.")
#
#
#     elif text == "Saved Files":
#
#         os.makedirs("ቁጥር", exist_ok=True)
#
#         weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#
#         # Create 7 day folders inside ቁጥር
#
#         for day in weekdays:
#             day_folder = os.path.join("ቁጥር", day)
#
#             os.makedirs(day_folder, exist_ok=True)
#
#         # Now ONLY use weekdays for showing buttons
#
#         keyboard = [["Main Menu"]]  # Always add Main Menu first
#
#         # Arrange weekdays 2 per row
#
#         row = []
#
#         for day in weekdays:
#
#             row.append(day)
#
#             if len(row) == 2:
#                 keyboard.append(row)
#
#                 row = []
#
#         if row:
#             keyboard.append(row)
#
#         reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
#
#         await update.message.reply_text("Select a day:", reply_markup=reply_markup)
#
#     elif text == "Main Menu":
#         keyboard = [["Add File", "Saved Files"]]
#         reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
#         await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
#
#     elif text in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
#         # If user clicks on a weekday, show message
#         await update.message.reply_text(f"You selected {text}. (Feature to upload into specific day coming soon!)")
#
#     else:
#         await update.message.reply_text("Invalid option. Please use the buttons.")
#
#
# async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     file = update.message.document or update.message.photo[-1]
#     file_id = file.file_id
#     file_name = file.file_name if hasattr(file, "file_name") else "image.jpg"
#
#     new_file = await context.bot.get_file(file_id)
#     os.makedirs("ቁጥር", exist_ok=True)
#     file_path = os.path.join("ቁጥር", file_name)
#
#     await new_file.download_to_drive(file_path)
#     await update.message.reply_text(f"File saved in 'ቁጥር' directory as: {file_name}")
#
#
# # (Old callbacks - you don't really use these now but keeping safe for future)
# async def show_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     await query.edit_message_text("Feature moved to buttons. Use the keyboard buttons.")
#
# async def add_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     await query.edit_message_text("Please send the file you want to upload.")
#
# async def send_saved_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     await query.edit_message_text("Feature moved to buttons. Use the keyboard buttons.")
#
#
# if __name__ == '__main__':
#     app = ApplicationBuilder().token(TOKEN).build()
#
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
#     app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_buttons))
#     app.add_handler(CallbackQueryHandler(show_file, pattern="^ቁጥር$"))
#     app.add_handler(CallbackQueryHandler(add_file_handler, pattern="^add_file$"))
#     app.add_handler(CallbackQueryHandler(send_saved_file, pattern="^file_"))
#
#     print("Bot is running...")
#     app.run_polling()
