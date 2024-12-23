from datetime import datetime, timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 
    
class Field:
    pass

class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        self.value = value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return True
        return False

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value.strftime("%d.%m.%Y")
        return None

class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        self.records[record.name.value] = record

    def find(self, name):
        return self.records.get(name)

    def get_upcoming_birthdays(self, days=7):
        upcoming = []
        today = datetime.now().date()
        for record in self.records.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year).date()
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if today <= birthday_this_year <= today + timedelta(days=days):
                    upcoming.append(record.name.value)
        return upcoming

def input_error(func):
    def wrapper(args, book):
        try:
            return func(args, book)
        except (IndexError, KeyError, ValueError) as e:
            return f"Error: {str(e)}"
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name = args[0]
    phone = args[1] if len(args) > 1 else None
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.change_phone(old_phone, new_phone):
        return "Phone number updated."
    return "Phone number not found."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    return "Contact not found."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.show_birthday():
        return record.show_birthday()
    return "No birthday found."

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays: " + ', '.join(upcoming_birthdays)
    return "No upcoming birthdays."

def parse_input(user_input):
    parts = user_input.split(maxsplit=1)
    command = parts[0]
    args = parts[1].split() if len(parts) > 1 else []
    return command, args

def main():
    book = load_data()  

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            for name, record in book.records.items():
                phones = ', '.join(phone.value for phone in record.phones)
                birthday = record.show_birthday() or "No birthday"
                print(f"Name: {name}, Phones: {phones}, Birthday: {birthday}")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

