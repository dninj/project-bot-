import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Словарь для хранения привычек пользователей (в реальном приложении хранилось бы в базе данных)
user_habits = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-трекер привычек. Начни с /add, чтобы добавить привычку.")


async def add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("Введи название привычки:")
    context.user_data['state'] = 'add_habit_name'


async def save_habit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habit_name = update.message.text
    user_habits[user_id] = user_habits.get(user_id, {})
    user_habits[user_id][habit_name] = {'completed': 0} # Инициализация с 0 выполненных раз
    await update.message.reply_text(f"Привычка '{habit_name}' добавлена! Используйте /track чтобы отслеживать.")
    context.user_data.pop('state') # Очищаем состояние


async def track_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        await update.message.reply_text("У тебя ещё нет привычек. Добавь их с помощью /add")
        return

    keyboard = []
    for habit_name in user_habits[user_id]:
        keyboard.append([InlineKeyboardButton(habit_name, callback_data=habit_name)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери привычку:", reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    habit_name = query.data
    user_habits[user_id][habit_name]['completed'] += 1
    await query.answer() # подтверждение нажатия
    await query.edit_message_text(text=f"Привычка '{habit_name}' отмечена как выполненная. Всего выполнено {user_habits[user_id][habit_name]['completed']} раз.")


def main():
    application = ApplicationBuilder().token("твой токен").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_habit))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_name)) #Обрабатывает только текстовые сообщения, которые не команды
    application.add_handler(CommandHandler("track", track_habit))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
