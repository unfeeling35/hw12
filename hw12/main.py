from collections import UserDict
import re
from datetime import datetime, timedelta
import json


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self._value)


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
        self._value = new_value

    @staticmethod
    def validate(phone):
        return re.fullmatch(r'\d{10}', phone) is not None


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        if not self.validate(new_value):
            raise ValueError("Birthday must be in YYYY-MM-DD format")
        self._value = new_value

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
        self.birthday = Birthday(birthday)
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
    def __init__(self, filename="phonebook.json"):
        super().__init__()
        self.filename = filename
        self.load_data()

    def __del__(self):
        self.save_data()

    def load_data(self):
        try:
            with open(self.filename, "r") as file:
                loaded_data = json.load(file)
                for name, value in loaded_data.items():
                    name_obj = Name(name)
                    record = Record(name_obj)
                    if 'birthday' in value:
                        record.birthday = Birthday(value['birthday'])
                    for phone in value.get('phones', []):
                        record.add_phone(phone)
                    self.data[name] = record
        except FileNotFoundError:
            self.data = {}

    def save_data(self):
        to_save = {}
        for name, record in self.data.items():
            record_data = {}
            if record.birthday.value:
                record_data['birthday'] = record.birthday.value
            record_data['phones'] = [phone.value for phone in record.phones]
            to_save[name] = record_data
        with open(self.filename, "w") as file:
            json.dump(to_save, file, ensure_ascii=False, indent=4)

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
