import sqlite3
import hmac
from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message
import re
from datetime import *
import rsaidnumber


class User(object):
    def __init__(self, user_id, email, password):
        self.id = user_id
        self.email = email
        self.password = password


class Posts(object):
    def __init__(self):
        self.conn = sqlite3.connect('twitter.db')
        self.cursor = self.conn.cursor()

    def add_desc(self, value):
        desc = "INSERT INTO tweets (description) VALUES (?)"
        self.cursor.execute(desc, dict(value))

    def add_image(self, value):
        image = "INSERT INTO tweets (image) VALUES (?)"
        self.cursor.execute(image, value)

    def second_image(self, value):
        image_two = "INSERT INTO tweets (image_two) VALUES (?)"
        self.cursor.execute(image_two, value)

    def third_image(self, value):
        image_three = "INSERT INTO tweets (image_three) VALUES (?)"
        self.cursor.execute(image_three, value)

    def fourth_image(self, value):
        image_four = "INSERT INTO tweets (image_four) VALUES (?)"
        self.cursor.execute(image_four, value)

    def commit(self):
        self.conn.commit()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# function that creates user table
def create_user():
    conn = sqlite3.connect('twitter.db')
    print('Database Successfully Created')

    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT,"
                 "last_name TEXT,"
                 "email TEXT UNIQUE,"
                 "cell_num TEXT,"
                 "id_num TEXT,"
                 "password TEXT,"
                 "profile_pic TEXT,"
                 "bio TEXT,"
                 "username TEXT UNIQUE,"
                 "following TEXT,"
                 "follower TEXT)")
    print("User Table Created Successfully")
    conn.close()


# function that creates the tweet table
def create_tweet():
    conn = sqlite3.connect('twitter.db')

    conn.execute("CREATE TABLE IF NOT EXISTS tweets (tweet_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "description TEXT,"
                 "image TEXT,"
                 "image_two TEXT,"
                 "image_three TEXT,"
                 "image_four TEXT,"
                 "date TEXT NOT NULL,"
                 "FOREIGN KEY (tweet_id) REFERENCES users(user_id))")
    print("Tweets Table Successfully Created")
    conn.close()


# function that creates the comments table
def create_comments():
    conn = sqlite3.connect('twitter.db')

    conn.execute("CREATE TABLE IF NOT EXISTS comments (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "description TEXT,"
                 "image TEXT,"
                 "date TEXT NOT NULL,"
                 "FOREIGN KEY (comment_id) REFERENCES tweets(tweet_id))")
    print("Comments Table Successfully Created")
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
user_id_table = {u.id: u for u in users}


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
app.config['MAIL_USERNAME'] = 'bigbirdonline25@gmail.com'
app.config['MAIL_PASSWORD'] = 'lifechoices1234'
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
        rsa_id = rsaidnumber.parse(request.json['id_num'])
        age = str((datetime.today() - rsa_id.date_of_birth) // timedelta(days=365.25))
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

        if len(name) == 0 or len(surname) == 0 or len(email) == 0 or len(new_num) == 0 or len(new_id) == 0 or len(
                password) == 0 or pic == 0 or len(bio) == 0 or len(username) == 0:
            raise Exception('Please ensure that each section is filled in correctly')
        elif int(age) < 18:
            raise Exception('You Are too Young to register. Please comeback when you are 18')
        elif rsa_id.valid is False:
            raise Exception('Please Enter A Valid ID Number')
        elif type(name) == int or type(surname) == int or type(pic) == int:
            raise TypeError("Please Use The Correct Values for Each Section")
        elif type(number) == str or type(id_num) == str:
            raise TypeError('Please Use The Correct Values for Each Section')
        else:
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
                                   "username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (first_name, last_name, email, cell_num, id_num, password, pic, bio, username))

                    conn.commit()

                    # initialising flask mail
                    mail = Mail(app)

                    # content of the email
                    msg = Message("User Registration Details", sender='bigbirdonline25@gmail.com', recipients=[email])
                    msg.body = "Thank You For Registering With Big Bird Online!" + "\n" + "\n" + "Your Details " \
                                                                                                 "Are As " \
                                                                                                 "Follows:" + \
                               "\n" + "\n" + "Username:" + " " + \
                               email + "\n" + "Password:" + " " + password + "\n" + "\n" + "Thank You For Choosing Big Bird Online! Please " \
                                                                                           "Enjoy The Experience! "

                    # sending the email
                    mail.send(msg)

                    global users

                    users = cursor.fetchall()

                    response['message'] = "You Have Successfully Registered"
                    response['status_code'] = 201
                return response
    except ValueError:
        raise Exception('Form Filled in Incorrectly/Invalid ID Number')


@app.route('/user-data/<email>')
def get_data(email):
    response = {}

    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user WHERE email = ?", (email,))
        users = cursor.fetchone()

        response['data'] = users
        response['status_code'] = 200
        response['message'] = "Successfully retrieved User ID"
    return response


@app.route('/user-profile/<int:user_id>')
def get_user(user_id):
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

        users = cursor.fetchone()

        response['results'] = users
        response['message'] = "You Successfully Viewed The Profile"
        response['status_code'] = 201
    return response


@app.route('/edit-user/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    response = {}

    try:
        name = str(request.json['first_name'])
        surname = str(request.json['last_name'])
        email = str(request.json['email'])
        phone = str(request.json['cell_num'])
        id_num = str(request.json['id_num'])
        password = str(request.json['password'])
        bio = str(request.json['bio'])
        username = str(request.json['username'])

        if len(name) == 0 and len(surname) == 0 and len(email) == 0 and len(phone) == 0 and len(id_num) == 0 and len(
                password) == 0 and len(bio) == 0 and len(username) == 0:
            raise Exception('Please Fill In At Least One Field')
        elif type(name) == int and type(surname) == int and type(email) == int and type(phone) == int and type(
                id_num) == int and type(password) == int and type(bio) == int and type(username) == int:
            raise ValueError('Please Use The Correct Values for Each Section')
        else:
            if request.method == "PUT":
                with sqlite3.connect('twitter.db') as conn:
                    incoming_data = dict(request.json)
                    new_data = {}

                    if incoming_data.get('first_name') is not None:
                        new_data['first_name'] = incoming_data.get('first_name')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET first_name = ? WHERE user_id=?",
                                           (new_data['first_name'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('last_name') is not None:
                        new_data['last_name'] = incoming_data.get('last_name')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET last_name =? WHERE user_id =?",
                                           (new_data['last_name'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('email') is not None:
                        new_data['email'] = incoming_data.get('email')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET email =? WHERE user_id =?", (new_data['email'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('cell_num') is not None:
                        new_data['cell_num'] = incoming_data.get('cell_num')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET cell_num =? WHERE user_id =?",
                                           (new_data['cell_num'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('password') is not None:
                        new_data['password'] = incoming_data.get('password')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET password =? WHERE user_id =?",
                                           (new_data['password'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('profile_pic') is not None:
                        new_data['profile_pic'] = incoming_data.get('profile_pic')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET profile_pic =? WHERE user_id =?",
                                           (new_data['profile_pic'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('bio') is not None:
                        new_data['bio'] = incoming_data.get('bio')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET bio =? WHERE user_id =?",
                                           (new_data['bio'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200

                    if incoming_data.get('username') is not None:
                        new_data['username'] = incoming_data.get('username')
                        print(new_data, incoming_data)
                        with sqlite3.connect('twitter.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET username =? WHERE user_id =?",
                                           (new_data['username'], user_id))
                            conn.commit()

                            response['message'] = "You successfully updated the user"
                            response['status_code'] = 200
                return response
    except ValueError:
        raise Exception('Please Fill in the form correctly')


@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    response = {}

    if request.method == "POST":
        with sqlite3.connect('twitter.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id =?", (user_id,))
            conn.commit()

            response['message'] = "You successfully deleted the user"
            response['status_code'] = 201
        return response


@app.route('/add-post/<int:user_id>', methods=['POST'])
def add_post(user_id):
    response = {}

    if request.method == 'POST':
        with sqlite3.connect('twitter.db') as conn:
            incoming_data = dict(request.json)
            new_data = {}

            if incoming_data.get('description') is not None:
                new_data['description'] = incoming_data.get('description')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO tweets (description, date) VALUES (?, ?)",
                                   (new_data['description'], now))
                    conn.commit()

                    response['message'] = "You successfully added a post"
                    response['status_code'] = 201

            if incoming_data.get('image') is not None:
                new_data['image'] = incoming_data.get('image')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO tweets (image, date) VALUES (?, ?)", (new_data['image'], now))
                    conn.commit()

            if incoming_data.get('image_two') is not None:
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()

                    cursor.execute("INSERT INTO tweets (image_two, date) VALUES (?, ?)", (new_data['image_two'], now))
                    conn.commit()

            if incoming_data.get('image_three') is not None:
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()

                    cursor.execute("INSERT INTO tweets (image_three, date) VALUES (?, ?)",
                                   (new_data['image_three'], now))
                    conn.commit()

            if incoming_data.get('image_three') is not None:
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()

                    cursor.execute("INSERT INTO tweets (image_three, date) VALUES (?, ?)",
                                   (new_data['image_three'], now))
                    conn.commit()

            if incoming_data.get('image_three') is not None:
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()

                    cursor.execute("INSERT INTO tweets (image_three, date) VALUES (?, ?)",
                                   (new_data['image_three'], now))
                    conn.commit()
        return response


@app.route('/edit-post/<int:user_id>/<int:tweet_id>', methods=['PUT'])
def edit_post(user_id, tweet_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('twitter.db') as conn:
            incoming_data = dict(request.json)
            new_data = {}

            if incoming_data.get('description') is not None:
                new_data['description'] = incoming_data.get('description')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tweets SET description = ? WHERE tweet_id = ?",
                                   (new_data['description'], tweet_id))
                    conn.commit()

                    response['message'] = "You updated the post successfully"
                    response['status_code'] = 201

            if incoming_data.get('image') is not None:
                new_data['image'] = incoming_data.get('image')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tweets SET image = ? WHERE tweet_id = ?", (new_data['image'], tweet_id))
                    conn.commit()

                    response['message'] = "You updated the post successfully"
                    response['status_code'] = 201

            if incoming_data.get('image_two') is not None:
                new_data['image_two'] = incoming_data.get('image_two')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tweets SET image_two =? WHERE  tweet_id =?",
                                   (new_data['image_two'], tweet_id))
                    conn.commit()

                    response['message'] = "You updated the post successfully"
                    response['status_code'] = 201

            if incoming_data.get('image_three') is not None:
                new_data['image_three'] = incoming_data.get('image_three')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tweets SET image_three =? WHERE  tweet_id =?",
                                   (new_data['image_three'], tweet_id))
                    conn.commit()

                    response['message'] = "You updated the post successfully"
                    response['status_code'] = 201

            if incoming_data.get('image_four') is not None:
                new_data['image_four'] = incoming_data.get('image_four')
                print(new_data, incoming_data)
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tweets SET image_four =? WHERE tweet_id =?",
                                   (new_data['image_four'], tweet_id))
                    conn.commit()

                    response['message'] = "You updated the post successfully"
                    response['status_code'] = 201
        return response


@app.route('/delete-post/<int:user_id>/<int:tweet_id>', methods=['POST'])
def delete_post(user_id, tweet_id):
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tweets where tweet_id = ?", (tweet_id,))
        conn.commit()

        response['message'] = "You successfully deleted the post"
        response['status_code'] = 201
    return response


@app.route('/user-posts/<int:user_id>')  # viewing user specific tweets
def view_posts(user_id):
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute("SELECT tweets.*, first_name FROM tweets AS tweets INNER JOIN users as users WHERE user_id = ?",
                       (user_id,))

        posts = cursor.fetchall()

        response['results'] = posts
        response['message'] = "You successfully views your posts"
        response['status_code'] = 201
    return response


@app.route('/all-posts')  # viewing all the posts made by everyone
def get_posts():
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tweets")

        posts = cursor.fetchall()

        response['results'] = posts
        response['message'] = "Viewed Post"
        response['status_code'] = 201
    return response


@app.route('/add-comment/<int:user_id>/post/<int:user_id2>/comment/<int:tweet_id>', methods=['POST'])
def add_comment(user_id, user_id2, tweet_id):
    response = {}

    if request.method == 'POST':
        with sqlite3.connect('twitter.db') as conn:
            incoming_data = dict(request.json)
            new_data = {}

            if incoming_data.get('description') is not None:
                new_data['description'] = incoming_data.get('description')
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO comments (description, tweet_id, date) VALUES (?, ?, ?)",
                                   (new_data['description'], now, tweet_id))
                    conn.commit()

                    response['message'] = "You successfully commented on a post"
                    response['status_code'] = 201

            if incoming_data.get('image') is not None:
                new_data['image'] = incoming_data.get('image')
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO comments (image, tweet_id, date) VALUES (?, ?, ?)",
                                   (new_data['image'], tweet_id, now))
                    conn.commit()

                    response['message'] = "Successful"
                    response['status_code'] = 201
        return response


@app.route('/get-comment/<int:user_id>/post/<int:user_id2>/comment/<int:tweet_id>')
def get_user_comments(user_id, user_id2, tweet_id):
    response = {}

    if request.method == 'GET':
        with sqlite3.connect('twitter.db') as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT comments.*, tweets.* FROM comments AS tweets INNER JOIN comments as users WHERE '
                           'tweet_id = ?', (tweet_id,))
            comments = cursor.fetchall()

            response['results'] = comments
            response['message'] = "Successfully viewed comments"
            response['status_code'] = 201
        return response


@app.route('/edit-comment/<int:user_id>/post/<int:user_id2>/post/<int:tweet_id>/comment/<int:comment_id>',
           methods=['PUT'])
def edit_comment(user_id, user_id2, tweet_id, comment_id):
    response = {}

    if request.method == 'PUT':
        with sqlite3.connect('twitter.db') as conn:
            incoming_data = dict(request.json)
            new_data = {}

            if incoming_data.get('description') is not None:
                new_data['description'] = incoming_data.get('description')
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE comments SET description = ?, date = ? WHERE comment_id =?",
                                   (new_data['description'], now, comment_id))
                    conn.commit()

                    response['message'] = "You successfully commented on a post"
                    response['status_code'] = 201

            if incoming_data.get('image') is not None:
                new_data['image'] = incoming_data.get('image')
                with sqlite3.connect('twitter.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE comments SET image = ?, date = ? WHERE comment_id =?", (new_data['image'],
                                                                                                   comment_id, now))
                    conn.commit()

                    response['message'] = "Successful"
                    response['status_code'] = 201
        return response


@app.route('/delete-comment/<int:user_id>/post/<int:user_id2>/comment/<int:comment_id>', methods=['POST'])
def remove_comment(user_id, user_id2, comment_id):
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comments where comment_id = ?", (comment_id,))
        conn.commit()

        response['message'] = "You successfully deleted the comment"
        response['status_code'] = 201
    return response


@app.route('/all-comments')
def get_comments():
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM comments")
        comments = cursor.fetchall()

        response['results'] = comments
        response['message'] = "Successfully retrieved all the comments"
        response['status_code'] = 201
    return response


@app.route('/user-profile/<int:user_id>/follow/<int:user_id2>', methods=['PATCH'])
def follow(user_id, user_id2):
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id =?", (user_id,))

        results = cursor.fetchone()

    try:
        if results['following'] is not None:
            following = list(map(int, results['following'].split()))
            following.append(user_id)
            converted_following = str(following)

            with sqlite3.connect('twitter.db') as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()

                cursor.execute("UPDATE users SET following = ? WHERE user_id = ?", (converted_following, user_id,))
                conn.commit()

                response['message'] = "You have successfully followed someone"
                response['status_code'] = 201

        if results['follower'] is not None:
            followers = list(map(int, results['follower'].split()))
            followers.append(user_id2)
            converted_followers = str(followers)

            with sqlite3.connect('twitter.db') as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()

                cursor.execute("UPDATE users SET follower = ? WHERE user_id = ?", (converted_followers, user_id2,))
                conn.commit()

                response['message'] = "successfully added user to followers"
                response['status_code'] = 201
        return response
    except ValueError:
        raise Exception('Data Not Being Stored Correctly')


@app.route('/user-profile/<int:user_id>/unfollow/<int:user_id2>', methods=['PATCH'])
def unfollow(user_id, user_id2):
    response = {}

    with sqlite3.connect('twitter.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        conn.commit()

        results = cursor.fetchone()

    if results['following'] is not None:
        following = list(map(int, results['following'].split()))
        following.remove(user_id)
        converted_following = str(following)

        with sqlite3.connect('twitter.db') as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET follower = ? WHERE user_id = ?", (converted_following, user_id,))
            conn.commit()

            response['message'] = "You have successfully unfollowed someone"
            response['status_code'] = 201

        if results['follower'] is not None:
            followers = list(map(int, results['follower'].split()))
            followers.remove(user_id2)
            converted_followers = str(followers)

            with sqlite3.connect('twitter.db') as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()

                cursor.execute("UPDATE users SET follower = ? WHERE user_id = ?", (converted_followers, user_id2,))
                conn.commit()

                response['message'] = "successfully removed user from followers"
                response['status_code'] = 201
        return response


@app.route('/view-followers/<int:user_id>')
def get_follower(user_id):
    response = {}

    if request.method == 'GET':
        with sqlite3.connect('twitter.db') as conn:
            cursor = conn.cursor()

            conn.row_factory = sqlite3.Row

            cursor.execute("SELECT follower FROM users WHERE user_id = ?", (user_id,))

            users = cursor.fetchall()

            response['results'] = users
            response['message'] = "You Successfully Viewed The Profile"
            response['status_code'] = 201
        return response


@app.route('/view-following/<int:user_id>')
def get_following(user_id):
    response = {}

    if request.method == 'GET':
        with sqlite3.connect('twitter.db') as conn:
            cursor = conn.cursor()

            conn.row_factory = sqlite3.Row

            cursor.execute("SELECT following FROM users WHERE user_id=?", (user_id,))

            found_users = cursor.fetchall()

            response['results'] = found_users
            response['message'] = "You Successfully Viewed The Profile"
            response['status_code'] = 201
        return response


if __name__ == '__main__':
    app.run(debug=True)
