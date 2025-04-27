import os
from telegram import Update, ReplyKeyboardMarkup
# from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ApplicationBuilder, ContextTypes, filters # type: ignore

TOKEN = "7945188969:AAGqv31lZK0YaRjVTDqBXgTiCJyt1hyICnc"  # Replace with your token!

# Create the ቁጥር directory if it doesn't exist
os.makedirs("ቁጥር", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Add File", "Saved Files"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)


async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Add File":
        await update.message.reply_text("Please send the file to upload (0 to 50MB).")
    elif text == "Saved Files":
        files = os.listdir("ቁጥር") if os.path.exists("ቁጥር") else []
        keyboard = [["Main Menu"]]  # Add Main Menu as the first button

        if files:
            # Add files as buttons
            for file in files:
                keyboard.append([file])  # Each file gets its own row
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("Select a file:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("No files found. Please upload a file first.")
    elif text in os.listdir("ቁጥር"):
        file_path = os.path.join("ቁጥር", text)
        if os.path.exists(file_path):
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, "rb"))
        else:
            await update.message.reply_text("File not found.")
    elif text == "Main Menu":
        await start(update, context)
    else:
        await update.message.reply_text("Invalid option. Please use the buttons.")
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1]
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else "image.jpg"

    new_file = await context.bot.get_file(file_id)
    file_path = os.path.join("ቁጥር", file_name)

    await new_file.download_to_drive(file_path)
    await update.message.reply_text(f"File saved in 'ቁጥር' directory as: {file_name}")

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
