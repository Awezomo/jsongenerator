import datetime
import random
import time
from faker import Faker
import markovify
from random_username.generate import generate_username

import numpy as np
import random

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

def handle_persons(data=None, attributes=None, num_records=None, action='generate'):
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # Flatten nested list if action is 'anonymize'
    if action == 'anonymize':
        if isinstance(data, list) and isinstance(data[0], list):
            data = data[0]  # Get the actual data from the first element of the outer list
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")
    

    firstname_generated = None
    lastname_generated = None
    user_num = fake.random_int(min=1, max=9999)
    email_domains = ['gmail.com', 'aon.at', 'gmx.at', 'outlook.com']
    results_times = []

    if action == 'generate':
        data = []
    
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]
        start_time = time.time()

        for attribute in attributes:
            if attribute == 'firstName':
                if not firstname_generated:
                    firstname_generated = fake.first_name()
                record[attribute] = firstname_generated
            elif attribute == 'lastName':
                if not lastname_generated:
                    lastname_generated = fake.last_name()
                record[attribute] = lastname_generated
            elif attribute == 'userName':
                include_number = np.random.choice([True, False], p=[0.7, 0.3])
                random_number = user_num if include_number else ""
                if firstname_generated:
                    first_name = firstname_generated
                    last_name = lastname_generated
                else:
                    firstname_generated = fake.first_name()
                    first_name = firstname_generated

                    lastname_generated = fake.last_name()
                    last_name = lastname_generated
                
                record[attribute] = f"{first_name.lower()}{last_name.lower()}{random_number}"
            elif attribute == 'email':
                first_name = firstname_generated or fake.first_name()
                last_name = lastname_generated or fake.last_name()
                include_number = np.random.choice([True, False], p=[0.9, 0.1])
                random_number = user_num if include_number else ""
                domain = random.choice(email_domains)
                record[attribute] = f"{first_name.lower()}.{last_name.lower()}{random_number}@{domain}"
            elif attribute == 'password':
                include_number = np.random.choice([True, False], p=[0.1, 0.9])
                record[attribute] = "12345678" if include_number else fake.password()
            elif attribute == 'birthDate':
                start_date = datetime.date(1950, 1, 1)
                end_date = datetime.date(2006, 12, 31)
                record[attribute] = str(fake.date_between(start_date=start_date, end_date=end_date))
            elif attribute == 'badgeName':
                record[attribute] = fake.word()
            elif attribute == 'badgeDescription':
                record[attribute] = fake.text()
            elif attribute == 'badgeIssuedOn':
                start_date = datetime.date(2000, 1, 1)
                end_date = datetime.date(2023, 12, 31)
                record[attribute] = str(fake.date_between(start_date=start_date, end_date=end_date))
            elif attribute == 'address':
                record[attribute] = fake.address()
            elif attribute == 'phone_number':
                record[attribute] = fake.phone_number()
            elif attribute == 'company':
                record[attribute] = fake.company()
            elif attribute == 'job':
                record[attribute] = fake.job()
            else:
                record[attribute] = fake.word()
        
        end_time = time.time()
        results_times.append(end_time - start_time)
        
        if action == 'generate':
            data.append(record)
    
    return data, results_times

def train_markov_model(uploaded_data, attribute):
    if uploaded_data is None:
        return None
    
    text = ""
    for data in uploaded_data:
        if attribute in data:
            text += data[attribute] + " "

    if not text:
        return None
    
    return markovify.Text(text)



def extract_attributes(uploaded_data):
    attributes = []
    if uploaded_data:
        attributes = list(uploaded_data[0].keys())
    return attributes



def generate_data_mf(uploaded_data, num_records=1):
    if not uploaded_data:
        return None

    attributes = extract_attributes(uploaded_data)
    results = []
    selected_badges = set()

    while len(results) < num_records:
        selected_record = random.choice(uploaded_data)
        badge_name = selected_record['badgeName']

        if badge_name not in selected_badges:
            result = {}

            for attribute in attributes:
                model = train_markov_model([selected_record], attribute)
                if model is not None:
                    generated_word = model.make_sentence(tries=100, test_output=False).strip()
                    if generated_word is None:
                        generated_word = fake.word()
                else:
                    generated_word = fake.word()

                # Add the generated description to the result
                result[attribute] = generated_word

            results.append(result)
            selected_badges.add(badge_name)

    return results
