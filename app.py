from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import time
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.users = []  # List to hold user details
        self.create_block(data={}, previous_hash='0')  # Genesis block with empty data

    def create_block(self, data, previous_hash=None):
        index = len(self.chain) + 1
        timestamp = time.time()
        block = Block(index, timestamp, data, previous_hash or self.get_latest_block().hash)
        self.chain.append(block)
        return block

    def get_latest_block(self):
        return self.chain[-1]

    def get_chain(self):
        return [block.__dict__ for block in self.chain]

    def add_blood_donation_record(self, donor_name, blood_type, quantity):
        data = {
            'donor_name': donor_name,
            'blood_type': blood_type,
            'quantity': quantity
        }
        return self.create_block(data, self.get_latest_block().hash)

    def view_records(self):
        return self.get_chain()

    def add_user(self, name, role, details):
        user = {
            'name': name,
            'role': role,
            'details': details
        }
        self.users.append(user)

    def view_users(self):
        return self.users

    def request_blood(self, patient_name, blood_type, quantity):
        # Search for available donations matching the blood type
        matching_records = [
            record for record in self.get_chain()
            if 'data' in record and 'blood_type' in record['data'] and record['data']['blood_type'] == blood_type
        ]

        if matching_records:
            return f"Blood request by {patient_name} for {quantity} units of blood type {blood_type} has been fulfilled."
        else:
            return f"No available blood of type {blood_type} for patient {patient_name}."

    def is_valid_blood_type(self, blood_type):
        valid_blood_types = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        return blood_type in valid_blood_types


# Initialize blockchain
blood_bank = Blockchain()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    role = request.form['role']
    details = request.form['details']
    blood_bank.add_user(name, role, details)
    flash(f"{role} registered successfully!")
    return redirect(url_for('index'))


@app.route('/add_donation', methods=['POST'])
def add_donation():
    donor_name = request.form['donor_name']
    blood_type = request.form['blood_type']
    quantity = int(request.form['quantity'])

    if not blood_bank.is_valid_blood_type(blood_type):
        flash("Invalid blood type entered. Please enter a valid blood type (A+, A-, B+, B-, AB+, AB-, O+, O-).")
        return redirect(url_for('index'))

    blood_bank.add_blood_donation_record(donor_name, blood_type, quantity)
    flash("Blood donation record added successfully!")
    return redirect(url_for('index'))


@app.route('/view_records')
def view_records():
    records = blood_bank.view_records()
    return render_template('view_records.html', records=records)


@app.route('/view_users')
def view_users():
    users = blood_bank.view_users()
    return render_template('view_users.html', users=users)


@app.route('/view_donors')
def view_donors():
    # Get all donor records from the blockchain
    donors = [record['data'] for record in blood_bank.get_chain() if 'donor_name' in record['data']]
    return render_template('view_donors.html', donors=donors)


@app.route('/view_patients')
def view_patients():
    # Get all registered patients from the blockchain
    patients = [user for user in blood_bank.view_users() if user['role'] == 'Patient']
    return render_template('view_patients.html', patients=patients)


@app.route('/request_blood', methods=['POST'])
def request_blood():
    patient_name = request.form['patient_name']
    blood_type = request.form['blood_type']
    quantity = int(request.form['quantity'])

    if not blood_bank.is_valid_blood_type(blood_type):
        flash("Invalid blood type entered. Please enter a valid blood type (A+, A-, B+, B-, AB+, AB-, O+, O-).")
        return redirect(url_for('index'))

    message = blood_bank.request_blood(patient_name, blood_type, quantity)
    flash(message)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)