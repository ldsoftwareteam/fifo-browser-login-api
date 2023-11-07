import os
from flask import Flask, request, jsonify

import bcrypt
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# MySQL Database Configuration



# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data['username']
#     password = data['password']

#     # Check if the username already exists
#     cursor.execute(f"SELECT * FROM browseruser.users WHERE username = '{username}'")
#     user = cursor.fetchone()

#     if user:
#         return jsonify({'message': 'Username already exists'}), 400

#     # Hash the password
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#     # Insert the new user into the database
#     cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
#     db.commit()

#     return jsonify({'message': 'User registered successfully'}), 201
@app.route('/', methods=['GET'])
def home():
    return{"message":"wlcome the the browser login api"}


@app.route('/login', methods=['POST'])
def login():
    # data = request.get_json()
    # username = data['username']
    # password = data['password']

    # Retrieve the user from the database
    # cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    # user = cursor.fetchone()

    # if user:
    #     stored_password = user[2]  # Assuming the hashed password is in the second column
    #     # salt = user[2]  # Assuming the salt is in the third column

    #     # Check if the provided password matches the stored password using the retrieved salt
    #     if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
    #         return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    # app.run(debug=True)