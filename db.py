class User:
    def __init__(self, firstname, telephone_number, email, password, role, created_at, children):
        self.firstname = firstname
        self.telephone_number = telephone_number
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at
        self.children = children

class Database:
    def __init__(self):
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    def get_user(self,login):
        for user in self.users:
            if user.telephone_number == login or user.email == login:
                return user
        return None
    def check_number(self, telephone_number):
        if len(telephone_number) != 9:
            return 2
        for user in self.users:
            if user.telephone_number == telephone_number:
                return 1

    def get_all_users(self):
        user_tb = []
        for user in self.users:
            user_tb.append(user)
        return user_tb

    def get_oldest(self):
        oldest_user = None
        for user in self.users:
            if oldest_user is None or user.created_at < oldest_user.created_at:
                oldest_user = user

        return oldest_user

    def get_kids(self):
        children = []
        for user in self.users:
            children.extend(user.children)

        return children

    def get_users(self, login):
        main_user = self.get_user(login)
        similar_users =[]
        for user in self.users:
            for child in user.children:
                for main_child in main_user.children:
                    if child['age'] == main_child['age'] and user.telephone_number != main_user.telephone_number:
                        similar_users.append(user)
                        break
        return similar_users