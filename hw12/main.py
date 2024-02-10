from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from collections import UserDict
import re
import json
from datetime import datetime, timedelta


class Field:
    def __init__(self, value=None):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value

    def __str__(self):
        return str(self.__value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    @Field.value.setter
    def value(self, new_value):
        if not self.validate(new_value):
            raise ValueError("Phone number must be 10 digits")
        self._Field__value = new_value

    @staticmethod
    def validate(phone):
        return re.fullmatch(r'\d{10}', phone) is not None


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        if not self.validate(new_value):
            raise ValueError("Birthday must be in YYYY-MM-DD format")
        self._Field__value = new_value

    @staticmethod
    def validate(birthday):
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError("Phone number not found")

    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    def days_to_birthday(self):
        if self.birthday.value is None:
            return None
        today = datetime.now()
        birthday_date = datetime.strptime(self.birthday.value, "%Y-%m-%d").replace(year=today.year)
        if birthday_date < today:
            birthday_date = birthday_date.replace(year=today.year + 1)
        return (birthday_date - today).days

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, n):
        records = list(self.data.values())
        for i in range(0, len(records), n):
            yield records[i:i + n]

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json_data = {key: record.__dict__ for key, record in self.data.items()}
            json.dump(json_data, file, default=lambda o: o.__dict__, indent=4)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            self.data = json.load(file)
            for key, record in self.data.items():
                name = record['name']['_Field__value']
                birthday = record.get('birthday', {}).get('_Field__value', None)
                record_obj = Record(name, birthday)
                for phone in record.get('phones', []):
                    record_obj.add_phone(phone['_Field__value'])
                self.data[key] = record_obj

    def search(self, query):
        result = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                result.append(record)
                continue
            for phone in record.phones:
                if query in phone.value:
                    result.append(record)
                    break
        return result


address_book = AddressBook()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я твой адресный бот. Введи /help чтобы увидеть доступные команды.')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = ('Доступные команды:\n'
                 '/start - начать работу\n'
                 '/help - вывести эту справку\n'
                 '/add_contact <имя> <телефон> [день рождения] - добавить контакт\n'
                 '/delete_contact <имя> - удалить контакт\n'
                 '/find_contact <имя> - найти контакт\n'
                 '/show_all - показать все контакты\n'
                 '/birthday <имя> - дни до дня рождения')
    await update.message.reply_text(help_text)


async def add_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name, phone, *birthday = context.args
        birthday = birthday[0] if birthday else None
        record = Record(name, birthday)
        record.add_phone(phone)
        address_book.add_record(record)
        await update.message.reply_text(f'Контакт {name} добавлен.')
    except ValueError as e:
        await update.message.reply_text(f'Ошибка при добавлении контакта: {e}')
    except Exception as e:
        await update.message.reply_text(f'Произошла ошибка: {e}')


async def delete_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = ' '.join(context.args)
        address_book.delete(name)
        await update.message.reply_text(f'Контакт {name} удален.')
    except KeyError:
        await update.message.reply_text('Контакт не найден.')


async def find_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = ' '.join(context.args)
    record = address_book.find(name)
    if record:
        await update.message.reply_text(str(record))
    else:
        await update.message.reply_text('Контакт не найден.')


async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacts = '\n'.join(str(record) for record in address_book.data.values())
    if contacts:
        await update.message.reply_text(contacts)
    else:
        await update.message.reply_text('Адресная книга пуста.')


async def birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = ' '.join(context.args)
    record = address_book.find(name)
    if record and record.birthday:
        days = record.days_to_birthday()
        await update.message.reply_text(f'До дня рождения {name} осталось {days} дней.')
    else:
        await update.message.reply_text('День рождения не указан или контакт не найден.')


def main():
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token('6785967564:AAGvbYxUsun_WNyGmZ9O8yhmCqiztHUhdyY').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('add_contact', add_contact))
    application.add_handler(CommandHandler('delete_contact', delete_contact))
    application.add_handler(CommandHandler('find_contact', find_contact))
    application.add_handler(CommandHandler('show_all', show_all))
    application.add_handler(CommandHandler('birthday', birthday))

    application.run_polling()


if __name__ == '__main__':
    main()
