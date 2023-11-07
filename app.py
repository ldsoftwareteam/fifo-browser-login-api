import os
from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# MySQL Database Configuration
mysql_url = os.environ.get('JAWSDB_URL')

# Parse the MySQL connection URL
url_parts = mysql_url.split("://")
if len(url_parts) == 2:
    driver, connection_info = url_parts
    user_pass, hostname_port_db = connection_info.split("@")
    username, password = user_pass.split(":")
    hostname, port_db = hostname_port_db.split(":")
    port, database_name = port_db.split("/")
else:
    print("Invalid MySQL URL format")
    exit(1)

# Connect to the MySQL database

db = mysql.connector.connect(
    user=username,
    password=password,
    host=hostname,
    port=int(port),
    database=database_name
)
# Create a cursor object to interact with the database
cursor = db.cursor()

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
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Retrieve the user from the database
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[2]  # Assuming the hashed password is in the second column
        # salt = user[2]  # Assuming the salt is in the third column

        # Check if the provided password matches the stored password using the retrieved salt
        # if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        #     return jsonify({'message': 'Login successful'}), 200
        if password == stored_password:
            return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    # app.run(debug=True)