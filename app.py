import json
from flask import Flask, request, jsonify
from datetime import datetime
import hashlib
import mysql.connector
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# MySQL Database Configuration
mysql_url = os.environ.get('JAWSDB_URL')
# print(mysql_url)

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
cursor = db.cursor(buffered=True)

# Check if the error_logs table exists, and create it if it doesn't
cursor.execute("""
CREATE TABLE IF NOT EXISTS error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    message TEXT NOT NULL,
    error TEXT NOT NULL,
    error_hash VARCHAR(64) NOT NULL,
    UNIQUE KEY unique_error (error_hash)
);
""")
db.commit()

# Check if the auto_error_logs table exists, and create it if it doesn't
cursor.execute("""
CREATE TABLE IF NOT EXISTS auto_error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    message TEXT NOT NULL,
    error TEXT NOT NULL,
    error_hash VARCHAR(64) NOT NULL,
    UNIQUE KEY unique_error (error_hash)
);
""")
db.commit()

# Home route
@app.route('/', methods=['GET'])
def home():
    return {"message": "Welcome to the browser error log API"}

# Route to handle error logs
@app.route('/log-errors', methods=['POST'])
def log_errors():
    try:
        data = request.get_json(force=True)
        # print("Raw data:", data)  # Debug statement

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            return jsonify({'message': 'Invalid data format'}), 400
        # print("Parsed data:", data)  # Debug statement

        for entry in data:
            # print("Processing entry:", entry, type(entry))  # Debug statement
            if not isinstance(entry, dict):
                return jsonify({'message': 'Invalid entry format'}), 400

            timestamp = entry.get('timestamp')
            message = entry.get('message')
            error = entry.get('error')

            if not (timestamp and message and error):
                return jsonify({'message': 'Invalid data'}), 400

            # Convert timestamp to datetime object
            try:
                timestamp_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return jsonify({'message': 'Invalid timestamp format'}), 400

            # Compute the hash of the error message
            error_hash = hashlib.sha256(error.encode()).hexdigest()

            # Check if the error already exists
            cursor.execute("SELECT id FROM error_logs WHERE error_hash = %s", (error_hash,))
            existing_error = cursor.fetchone()

            if existing_error:
                # Update existing log entry
                cursor.execute(
                    "UPDATE error_logs SET timestamp = %s, message = %s WHERE id = %s",
                    (timestamp_dt, message, existing_error[0])
                )
            else:
                # Insert new log entry
                cursor.execute(
                    "INSERT INTO error_logs (timestamp, message, error, error_hash) VALUES (%s, %s, %s, %s)",
                    (timestamp_dt, message, error, error_hash)
                )

        db.commit()
        return jsonify({'message': 'Error logs processed successfully'}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': 'An internal error occurred'}), 500

# Route to handle auto-generated error logs
@app.route('/log-auto-errors', methods=['POST'])
def log_auto_errors():
    try:
        data = request.get_json(force=True)
        # print("Raw data for auto errors:", data)  # Debug statement

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            return jsonify({'message': 'Invalid data format'}), 400
        # print("Parsed data for auto errors:", data)  # Debug statement

        for entry in data:
            # print("Processing entry for auto errors:", entry, type(entry))  # Debug statement
            if not isinstance(entry, dict):
                return jsonify({'message': 'Invalid entry format'}), 400

            timestamp = entry.get('timestamp')
            message = entry.get('message')
            error = entry.get('error')

            if not (timestamp and message and error):
                return jsonify({'message': 'Invalid data'}), 400

            # Convert timestamp to datetime object
            try:
                timestamp_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return jsonify({'message': 'Invalid timestamp format'}), 400

            # Compute the hash of the error message
            error_hash = hashlib.sha256(error.encode()).hexdigest()

            # Check if the error already exists in auto_error_logs
            cursor.execute("SELECT id FROM auto_error_logs WHERE error_hash = %s", (error_hash,))
            existing_error = cursor.fetchone()

            if existing_error:
                # Update existing log entry
                cursor.execute(
                    "UPDATE auto_error_logs SET timestamp = %s, message = %s WHERE id = %s",
                    (timestamp_dt, message, existing_error[0])
                )
            else:
                # Insert new log entry into auto_error_logs
                cursor.execute(
                    "INSERT INTO auto_error_logs (timestamp, message, error, error_hash) VALUES (%s, %s, %s, %s)",
                    (timestamp_dt, message, error, error_hash)
                )

        db.commit()
        return jsonify({'message': 'Auto error logs processed successfully'}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': 'An internal error occurred'}), 500

# Route to get error logs
@app.route('/get-errors', methods=['GET'])
def get_errors():
    try:
        cursor.execute("SELECT * FROM error_logs ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        error_logs = []
        for row in rows:
            error_logs.append({
                'id': row[0],
                'timestamp': row[1].isoformat(),
                'message': row[2],
                'error': row[3],
                'error_hash': row[4]
            })
        return jsonify({'error_logs': error_logs}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': 'An internal error occurred'}), 500

# Route to get auto-generated error logs
@app.route('/get-auto-errors', methods=['GET'])
def get_auto_errors():
    try:
        cursor.execute("SELECT * FROM auto_error_logs ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        auto_error_logs = []
        for row in rows:
            auto_error_logs.append({
                'id': row[0],
                'timestamp': row[1].isoformat(),
                'message': row[2],
                'error': row[3],
                'error_hash': row[4]
            })
        return jsonify({'auto_error_logs': auto_error_logs}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': 'An internal error occurred'}), 500

# Login route for example
@app.route('/login/v2', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Retrieve the user from the database
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[2]  # Assuming the hashed password is in the second column
        if password == stored_password:
            return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
