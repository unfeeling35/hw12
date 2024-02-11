from collections import UserDict
import re
from datetime import datetime
import json


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


def load_contacts(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            address_book = AddressBook()
            for name, record in data.items():
                new_record = Record(name, record.get('birthday'))
                for phone in record.get('phones', []):
                    new_record.add_phone(phone)
                address_book.add_record(new_record)
            return address_book
    except FileNotFoundError:
        return AddressBook()


def save_contacts(address_book, filename):
    data = {record.name.value: {"phones": [phone.value for phone in record.phones],
                                "birthday": record.birthday.value if record.birthday else None}
            for record in address_book.data.values()}
    with open(filename, 'w') as file:
        json.dump(data, file)


def input_error(handler):
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except KeyError:
            return "There is no such contact"
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter user name"
    return wrapper


@input_error
def add_contact(address_book, name, phone):
    if not name or not phone:
        raise ValueError("Give me name and phone please")
    if address_book.find(name):
        raise ValueError("Contact already exists")
    new_record = Record(name)
    new_record.add_phone(phone)
    address_book.add_record(new_record)
    return f"Contact {name} added"


@input_error
def change_contact(address_book, name, phone):
    if not name or not phone:
        raise ValueError("Give me name and phone please")
    record = address_book.find(name)
    if record is None:
        raise KeyError
    record.phones = []
    record.add_phone(phone)
    return f"Contact {name} updated"


@input_error
def show_phone(address_book, name):
    record = address_book.find(name)
    if record is None:
        raise KeyError
    return ', '.join([phone.value for phone in record.phones])


@input_error
def show_all_contacts(address_book):
    if not address_book:
        return "Contact list is empty"
    return "\n".join([str(record) for record in address_book.data.values()])


@input_error
def search_contact(address_book, query):
    if not query:
        raise ValueError("Please provide a search query")
    matching_contacts = []
    for record in address_book.values():
        if query.lower() in record.name.value.lower() or any(query in phone.value for phone in record.phones):
            matching_contacts.append(str(record))
    if not matching_contacts:
        return "No matching contacts found"
    return "\n".join(matching_contacts)


def main():
    filename = 'contacts.db'
    address_book = load_contacts(filename)

    while True:
        user_input = input(">").lower()
        command, *args = user_input.split(maxsplit=1)

        if command == "hello":
            print("How can I help you?")
        elif user_input in ["good bye", "close", "exit"]:
            print("Good bye!")
            save_contacts(address_book, filename)
            break
        elif command == "add":
            name, phone = (args[0].split() + [None, None])[:2]
            print(add_contact(address_book, name, phone))
        elif command == "change":
            name, phone = (args[0].split() + [None, None])[:2]
            print(change_contact(address_book, name, phone))
        elif command == "phone":
            name = args[0]
            print(show_phone(address_book, name))
        elif user_input == "show all":
            print(show_all_contacts(address_book))
        elif command == "search":
            query = args[0] if args else ""
            print(search_contact(address_book, query))
        else:
            print("Unknown command or wrong format")


if __name__ == "__main__":
    main()
