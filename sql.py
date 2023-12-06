import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect('my_database')
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS children (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES users (id)
                )
            ''')

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firstname TEXT NOT NULL,
                    telephone_number INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_children (
                    user_id INTEGER,
                    child_id INTEGER,
                    PRIMARY KEY (user_id, child_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (child_id) REFERENCES children (id)
                )
            ''')
        self.connection.commit()

    def display_users(self):
        self.cursor.execute('SELECT * FROM users')
        users = self.cursor.fetchall()
        for user in users:
            print(user)

    def display_children(self):
        self.cursor.execute('SELECT * FROM children')
        children = self.cursor.fetchall()
        for child in children:
            print(child)

    def display_user_children(self):
        self.cursor.execute('SELECT * FROM user_children')
        user_children = self.cursor.fetchall()
        for user_child in user_children:
            print(user_child)

    def add_user(self, firstname, telephone_number, email, password, role):
        self.cursor.execute('''
            INSERT INTO users (firstname, telephone_number, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (firstname, telephone_number, email, password, role))
        user_id = self.cursor.lastrowid

        num_children = int(input('Enter the number of children: '))
        for _ in range(num_children):
            child_name = input('Enter child name: ')
            child_age = int(input('Enter child age: '))

            self.cursor.execute('''
                INSERT INTO children (name, age, parent_id)
                VALUES (?, ?, ?)
            ''', (child_name, child_age, user_id))
            child_id = self.cursor.lastrowid

            self.cursor.execute('''
                INSERT INTO user_children (user_id, child_id)
                VALUES (?, ?)
            ''', (user_id, child_id))

        self.connection.commit()
        print(f'User {firstname} with {num_children} children added successfully.')

    def exit_database(self):
        self.connection.close()
        print('Exiting database.')
