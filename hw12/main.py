import json

class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, name, phone):
        self.contacts.append({'name': name, 'phone': phone})

    def save_to_disk(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.contacts, file)

    def load_from_disk(self, filename):
        with open(filename, 'r') as file:
            self.contacts = json.load(file)

    def search_contacts(self, query):
        return [contact for contact in self.contacts if query.lower() in contact['name'].lower() or query in contact['phone']]

# Використання
address_book = AddressBook()
address_book.add_contact('Denis Pa', '123456789')
address_book.add_contact('Vika Ber', '987654321')

# Збереження на диск
address_book.save_to_disk('address_book.json')

# Відновлення з диска
address_book.load_from_disk('address_book.json')

# Пошук
matches = address_book.search_contacts('Ber')
print(matches)
