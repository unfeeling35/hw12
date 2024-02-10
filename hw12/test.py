from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Определяем функции-обработчики команд
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\! Я твоя адресная книга\. Можешь добавить, найти или удалить контакты\. ',
        reply_markup=ForceReply(selective=True),
    )

def save_contact(update: Update, context: CallbackContext) -> None:
    text = update.message.text.partition(' ')[2]
    name, _, phone = text.partition(' ')
    try:
        record = Record(name)
        record.add_phone(phone)
        address_book.add_record(record)
        update.message.reply_text('Контакт успешно сохранен!')
    except Exception as e:
        update.message.reply_text(f'Ошибка при сохранении контакта: {e}')

def find_contact(update: Update, context: CallbackContext) -> None:
    query = update.message.text.partition(' ')[2]
    results = address_book.search(query)
    if results:
        response = '\n'.join([str(result) for result in results])
        update.message.reply_text(f'Найденные контакты:\n{response}')
    else:
        update.message.reply_text('Контакты не найдены.')

# Определяем функцию main
def main():
    updater = Updater("6785967564:AAGvbYxUsun_WNyGmZ9O8yhmCqiztHUhdyY")
    dispatcher = updater.dispatcher

    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("save", save_contact))
    dispatcher.add_handler(CommandHandler("find", find_contact))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
