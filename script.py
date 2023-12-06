import argparse
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import sqlite3
from sql import DatabaseManager
from db import Database, User

def get_json(filename):
    x = open(filename)
    data = json.load(x)
    return data

def get_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    data = []
    for user in root.findall('user'):
        firstname = user.find('firstname').text
        tel = user.find('telephone_number').text
        email = user.find('email').text
        password = user.find('password').text
        role = user.find('role').text
        created = user.find('created_at').text
        child_data = []
        for children in user.findall('children'):
            for child in children.findall('child'):
                name = child.find('name').text
                age = child.find('age').text
                child_dict = {'name' : name, 'age' : age}
                child_data.append(child_dict)

        dict_1 = {'firstname': firstname, 'telephone_number': tel, 'email': email, 'password': password,
        'role': role, 'created_at': created, 'children': child_data}
        data.append(dict_1)

    return data

def get_csv(filename):
    data = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            children_list = []
            children_data = row.get('children', '').split(',')
            for child_info in children_data:
                if child_info.strip():
                    name, age = child_info.strip().split(' ')
                    children_list.append({'name': name, 'age': age[1:-1]})

            row.pop('children', None)
            row['children'] = children_list

            data.append(row)

    return data

def phone_numbers(data):
    remove_numbers = []
    unique_numbers = []
    for i, dictionary in enumerate(data):
            if 'telephone_number' in dictionary:
                number = ''.join(letter for letter in str(dictionary['telephone_number']) if letter.isalnum())
                if len(number) < 9:
                    remove_numbers.append(i)
                    continue
                if len(number) >= 9:
                    above = len(number) - 9
                    number = number[above:]
                if number not in unique_numbers:
                    unique_numbers.append(number)
                    dictionary['telephone_number'] = number
                else:
                    first_index = unique_numbers.index(number)
                    first_time = datetime.strptime(data[first_index]['created_at'], "%Y-%m-%d %H:%M:%S")
                    current_time = datetime.strptime(dictionary['created_at'], "%Y-%m-%d %H:%M:%S")
                    data[i]['telephone_number'] = number
                    if data[first_index]['telephone_number'] == data[i]['telephone_number']:
                        pass
                    if current_time > first_time:
                        remove_numbers.append(first_index)
                        unique_numbers[first_index] = number
                    else:
                        remove_numbers.append(i)
            else:
                remove_numbers.append(i)

    for i in reversed(remove_numbers):
        data.pop(i)

    return data

def email_validation(data):

    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.([a-zA-Z0-9-]{1,4})$'
    wrong_mail = []
    if isinstance(data, str):
        if re.match(pattern,data):
            return True
        else:
            return False
    for i, dictionary in enumerate(data):
        mail = dictionary['email']
        if not re.match(pattern,mail):
            wrong_mail.append(i)

    for i in reversed(wrong_mail):
        data.pop(i)

    return data

def check_if_admin(login, password, database):
    if database.get_user(login):
        user = database.get_user(login)
    else:
        print('Invalid login, please try again')
        return

    if (user.telephone_number == login or user.email == login) and user.password == password:
        if user.role == 'admin':
            return True
        else:
            print('You need admin access')
    else:
        print('Invalid login or password, please try again')

def print_all_accounts_func(login, password, database):
    if check_if_admin(login, password, database):
        print(f'Number of all valid accounts: {len(database.get_all_users())}')
    else:
        return

def print_oldest_account_func(login, password, database):
    if check_if_admin(login, password, database):
        oldest = database.get_oldest()
        print(f'Name: {oldest.firstname}')
        print(f'email_address: {oldest.email}')
        print(f'created_at: {oldest.created_at}')

def group_by_age_func(login, password, database):
    if check_if_admin(login, password, database):
        children = database.get_kids()
        age_counts = {str(i): 0 for i in range(1, 19)}

        for child in children:
            if 'age' in child and isinstance(int(child['age']), int):
                age_counts[str(child['age'])] += 1
            else:
                print(f"Skipping invalid age: {child.get('age')}")

        sorted_age_counts = sorted(age_counts.items(), key=lambda x: int(x[0]), reverse=True)

        for age, count in sorted_age_counts:
            if count > 0:
                print(f'age: {age}, count: {count}')

def print_children_func(login, password, database):
    if database.get_user(login):
        user = database.get_user(login)
    children = user.children
    sorted_children = sorted(children, key=lambda x: x.get('name', '').lower())
    for child in sorted_children:
        print(f"{child['name']}, {child['age']}")

def find_similar_children_by_age_func(login, password, database):
    people = database.get_users(login)
    main_user = database.get_user(login)
    similar_children = []


    if not main_user.children:
        print('You have no children, therefore there is no match')
        return

    for user in people:
        matching_children = [child for child in user.children if
                             any(main_child['age'] == child['age'] for main_child in main_user.children)]

        if matching_children:
            sorted_children = sorted(matching_children, key=lambda x: x['name'].lower())
            other_children = [child for child in user.children if child not in matching_children]
            similar_children.append(
                {'parent_name': user.firstname,'telephone_number': user.telephone_number, 'matching_children': sorted_children, 'other_children': other_children})

    sorted_families = sorted(similar_children,
                             key=lambda x: (max(child['age'] for child in x['matching_children']), x['parent_name']))

    for family in sorted_families:
        parent_name = family['parent_name']
        matching_children_info = "; ".join(
            [f"{child['name']}, {child['age']}" for child in family['matching_children']])
        other_children_info = "; ".join([f"{child['name']}, {child['age']}" for child in family['other_children']])

        print(f"{parent_name}, {family['telephone_number']}: {matching_children_info}; {other_children_info}")

def create_database_func(login, password, database):
    if check_if_admin(login, password, database):
        database_manager = DatabaseManager()
        database_manager.create_tables()
        print('Database created.')

        while True:
            print('1. Display Users')
            print('2. Display Children')
            print('3. Display User Children')
            print('4. Add User')
            print('5. Exit')

            choice = input('Enter your choice: ')

            if choice == '1':
                database_manager.display_users()
            elif choice == '2':
                database_manager.display_children()
            elif choice == '3':
                database_manager.display_user_children()
            elif choice == '4':
                firstname = input('Enter firstname: ')
                telephone_number = input('Enter telephone number: ')
                if database.check_number(telephone_number) == 1:
                    print('Such a number already exists in our database')
                    continue
                elif database.check_number(telephone_number) == 2:
                    print('The number is too long, or too short, check our requirements: \n'
                          '1) No spaces between numbers\n'
                          '2) No special characters"(),+-"\n'
                          '3) No leading zeros\n\n')
                    continue
                email = input('Enter email: ')
                if email_validation(email) == False:
                    print('Wrong email address, check if your email meets our requirements: \n'
                          '1) Email must contain only one "@" symbol. \n'
                          '2) The part before "@" must be at least 1 character long.\n'
                          '3) The part between "@" and "." must be at least 1 character long.\n'
                          '4) The part after the last "." must be between 1 and 4 characters long,'
                          ' containing only letters and/or digits.\n\n')
                    continue
                password = input('Enter password: ')
                role = input('Enter role: ')
                database_manager.add_user(firstname, telephone_number, email, password, role)
            elif choice == '5':
                database_manager.exit_database()
                break
            else:
                print('Invalid choice. Please enter a number between 1 and 5.')

def fetch_data_from_sqlite():
    con = sqlite3.connect('my_database')
    cur = con.cursor()

    cur.execute("SELECT * FROM users")
    users_data = cur.fetchall()

    cur.execute("SELECT * FROM children")
    children_data = cur.fetchall()

    con.close()

    return users_data, children_data

def transform_data(users_data, children_data):
    transformed_data = []

    for user_row in users_data:
        user_dict = {
            'firstname': user_row[1],
            'telephone_number': user_row[2],
            'email': user_row[3],
            'password': user_row[4],
            'role': user_row[5],
            'created_at': user_row[6],
            'children': []
        }

        for child_row in children_data:
            if child_row[3] == user_row[0]:
                child_dict = {
                    'name': child_row[1],
                    'age': child_row[2]
                }
                user_dict['children'].append(child_dict)

        transformed_data.append(user_dict)

    return transformed_data


def main():
    parser = argparse.ArgumentParser(description='Hello it is my database, if you want to use it,'
                                                 ' type: <command> --login <login> --password <password>'
                                                 ', if your password includes any special sign, please put password in quotes')
    subparsers = parser.add_subparsers(title='commands', dest='command', help='Available commands')

    print_all_accounts_parser = subparsers.add_parser('print-all-accounts', help='Admin function to print all accounts')
    print_all_accounts_parser.add_argument('--login', required=True, type=str, help='Type your email or phone number(9 digits)')
    print_all_accounts_parser.add_argument('--password', required=True, type=str, help='Type your password')
    print_all_accounts_parser.set_defaults(func=print_all_accounts_func)

    print_oldest_account = subparsers.add_parser('print-oldest-account', help='Admin function to print oldest account')
    print_oldest_account.add_argument('--login', required=True, type=str,
                                      help='Type your email or phone number(9 digits)')
    print_oldest_account.add_argument('--password', required=True, type=str, help='Type your password')
    print_oldest_account.set_defaults(func=print_oldest_account_func)

    group_by_age = subparsers.add_parser('group-by-age', help='Admin function to group children by age')
    group_by_age.add_argument('--login', required=True, type=str,
                              help='Type your email or phone number(9 digits)')
    group_by_age.add_argument('--password', required=True, type=str, help='Type your password')
    group_by_age.set_defaults(func=group_by_age_func)

    print_children = subparsers.add_parser('print-children', help='User function to print all children details')
    print_children.add_argument('--login', required=True, type=str,
                                help='Type your email or phone number(9 digits)')
    print_children.add_argument('--password', required=True, type=str, help='Type your password')
    print_children.set_defaults(func=print_children_func)

    find_similar_children_by_age = subparsers.add_parser('find-similar-children-by-age',
                                                         help='User function to find all children similar by age')
    find_similar_children_by_age.add_argument('--login', required=True, type=str,
                                              help='Type your email or phone number(9 digits)')
    find_similar_children_by_age.add_argument('--password', required=True, type=str, help='Type your password')
    find_similar_children_by_age.set_defaults(func=find_similar_children_by_age_func)

    create_database = subparsers.add_parser('create-database',
                                            help='Create database in SQL which will be connected to database aalready included'
                                                 'in my program')
    create_database.add_argument('--login', required=True, type=str,
                                              help='Type your email or phone number(9 digits)')
    create_database.add_argument('--password', required=True, type=str, help='Type your password')
    create_database.set_defaults(func=create_database_func)

    args = parser.parse_args()

    database = Database()

    users_data, children_data = fetch_data_from_sqlite()
    transformed_data = transform_data(users_data, children_data)

    merged_data = get_csv('data/users_1.csv') + get_csv('data/users_2.csv') + get_json('data/users.json') + \
                  get_xml('data/users_2.xml') + get_xml('data/users_1.xml') + transformed_data

    phone_validation = phone_numbers(merged_data)
    validated_data_email = email_validation(phone_validation)

    for user_data in validated_data_email:
        user = User(**user_data)
        database.add_user(user)

    if hasattr(args, 'func'):
        args.func(args.login, args.password, database)
    else:
        print('Unknown function')

if __name__ == '__main__':
    main()
