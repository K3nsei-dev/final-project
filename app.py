import sqlite3
import hmac
from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message
import re
from datetime import *


class User(object):
    def __init__(self, user_id, email, password):
        self.user_id = user_id
        self.email = email
        self.password = password


# function that creates user table
def create_user():
    conn = sqlite3.connect('twitter.db')
    print('Database Successfully Created')

    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "cell_num TEXT NOT NULL,"
                 "id_num TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "profile_pic TEXT NOT NULL,"
                 "bio TEXT NOT NULL,"
                 "username TEXT NOT NULL)")
    print("User Table Created Successfully")
    conn.close()


# function that creates the tweet table
def create_tweet():
    conn = sqlite3.connect('twitter.db')

    conn.execute("CREATE TABLE IF NOT EXISTS tweets (tweet_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "description TEXT NOT NULL,"
                 "image TEXT NOT NULL,"
                 "date TEXT NOT NULL,"
                 "FOREIGN KEY (tweet_id) REFERENCES users(user_id))")
    print("Tweets Table Successfully Created")
    conn.close()


# function that creates the comments table
def create_comments():
    conn = sqlite3.connect('twitter.db')

    conn.execute("CREATE TABLE IF NOT EXISTS comments (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "description TEXT NOT NULL,"
                 "image TEXT NOT NULL,"
                 "date TEXT NOT NULL,"
                 "FOREIGN KEY (comment_id) REFERENCES tweets(tweet_id))")
    print("Comments Table Successfully Created")
    conn.close()


# function that creates the followers table
def create_followers():
    conn = sqlite3.connect('twitter.db')

    conn.execute("CREATE TABLE IF NOT EXISTS followers (follow_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "follow INTEGER NOT NULL,"
                 "following INTEGER NOT NULL,"
                 "FOREIGN KEY (follow_id) REFERENCES users(user_id))")
    print("Followers Table Created Successfully")
    conn.close()


# function that creates the direct message table
def create_dm():
    conn = sqlite3.connect('twitter.db')

    conn.execute("CREATE TABLE IF NOT EXISTS messages (direct_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "sent TEXT NOT NULL,"
                 "received TEXT NOT NULL,"
                 "date TEXT NOT NULL,"
                 "FOREIGN KEY (direct_id) REFERENCES users(user_id))")
    print("Direct Messages Table Created Successfully")
    conn.close()


# calling functions
create_user()
create_tweet()
create_comments()
create_followers()
create_dm()


# # calling data from users table
def fetch_users():
    with sqlite3.connect('twitter.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[6]))
    return new_data


# declaring users
users = fetch_users()

username_table = {u.email: u for u in users}
user_id_table = {u.user_id: u for u in users}


def authenticate(email, password):
    user = username_table.get(email, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(number):
    user_id = number['identity']
    return user_id_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'super-secret'
# flask send email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lca.pointofsale@gmail.com'
app.config['MAIL_PASSWORD'] = 'lifechoices2021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# date time variable
now = datetime.now()

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/register', methods=['POST'])
def register():
    response = {}

    regex_email = request.json['email']  # getting the email from the form

    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'  # regular expression for validating email

    # verifying email address
    if re.search(regex, regex_email):
        pass
    else:
        raise Exception("Invalid Email Address, Please Try Again!")

    try:
        name = str(request.json['first_name'])
        surname = str(request.json['last_name'])
        email = request.json['email']
        number = int(request.json['cell_num'])
        new_num = request.json['cell_num']
        id_num = int(request.json['id_num'])
        new_id = request.json['id_num']
        password = request.json['password']
        pic = str(request.json['profile_pic'])
        bio = request.json['bio']
        username = request.json['username']

        if len(name) == 0 or len(surname) == 0 or len(email) == 0 or len(new_num) == 0 or len(new_id) == 0 or len(password) == 0 or pic == 0 or len(bio) == 0 or len(username) == 0:
            raise Exception('Please ensure that each section is filled in correctly')
        elif type(name) == int or type(surname) == int or type(pic) == int:
            raise TypeError("Please Use The Correct Values for Each Section")
        elif type(number) == str or type(id_num) == str:
            raise TypeError('Please Use The Correct Values for Each Section')
        else:
            pass
    except ValueError:
        raise Exception('Incorrect Type Used For A Section')

    if request.method == 'POST':
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        email = request.json['email']
        cell_num = request.json['cell_num']
        id_num = request.json['id_num']
        password = request.json['password']
        pic = request.json['profile_pic']
        bio = request.json['bio']
        username = request.json['username']

        with sqlite3.connect('twitter.db') as conn:
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (first_name,"
                           "last_name,"
                           "email,"
                           "cell_num,"
                           "id_num,"
                           "password,"
                           "profile_pic,"
                           "bio,"
                           "username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (first_name, last_name, email, cell_num, id_num, password, pic, bio, username))

            conn.commit()

            global users

            users = cursor.fetchall()

            response['message'] = "You Have Successfully Registered"
            response['status_code'] = 201
        return response





if __name__ == '__main__':
    app.run(debug=True)
