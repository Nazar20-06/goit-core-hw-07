from datetime import datetime, date, timedelta
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        self.validate(value)
        parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        super().__init__(parsed_date)

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError("Birthday must be a string in DD.MM.YYYY format.")
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")
        if parsed_date > date.today():
            raise ValueError("Birthday cannot be in the future.")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old, new):
        for i, p in enumerate(self.phones):
            if p.value == old:
                self.phones[i] = Phone(new)
                return
        raise ValueError("Old phone not found.")

    def add_birthday(self, birthday_str):
        if self.birthday is not None:
            raise ValueError("Birthday is already set for this contact.")
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{self.name.value}: {phones}; Birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value.replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)

                delta = (bday - today).days
                if 0 <= delta <= 7:
                    # Переносимо на понеділок, якщо вихідний
                    if bday.weekday() == 5:
                        bday += timedelta(days=2)
                    elif bday.weekday() == 6:
                        bday += timedelta(days=1)

                    upcoming.append({
                        "name": record.name.value,
                        "birthday": bday.strftime("%d.%m.%Y")
                    })

        return upcoming

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, KeyError, ValueError, TypeError) as e:
            return f"Error: {str(e)}"
    return wrapper

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, args

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old, new = args
    record = book.find(name)
    if record:
        record.change_phone(old, new)
        return "Phone changed."
    raise ValueError("Contact not found.")

@input_error
def get_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join(p.value for p in record.phones)
    raise ValueError("Contact not found.")

@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.add_birthday(bday)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(get_phones(args, book))

        elif command == "all":
            print(show_all(book))

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
