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

# Function to generate structured data using Faker
def generate_json_data(attributes, num_records):

    # List of random email domains
    email_domains = ['gmail.com', 'aon.at', 'gmx.at', 'outlook.com']

    firstname_generated = None
    lastname_generated = None
    user_num = fake.random_int(min=1, max=9999)
    data = []
    results_times = []

    for _ in range(num_records):
        record = {}
        for attribute in attributes:
            if attribute == 'firstName':
                if firstname_generated is None:
                    record[attribute] = fake.first_name()
                else:
                    record[attribute] = firstname_generated
            elif attribute == 'lastName':
                if lastname_generated is None:
                    record[attribute] = fake.last_name()
                else:
                    record[attribute] = lastname_generated
            elif attribute == 'userName':
                # Randomly decide whether to include a number
                
                # Randomly decide between using name-based or random username
                if random.choice([True, False]):
                    include_number = np.random.choice([True, False], p=[0.7, 0.3])
                    random_number = user_num if include_number else ""
        
                    first_name = record.get('firstName', fake.first_name())
                    last_name = record.get('lastName', fake.last_name())
                    firstname_generated = first_name
                    lastname_generated = last_name
                    record[attribute] = f"{first_name.lower()}{last_name.lower()}{random_number}"
                else:
                    record[attribute] = f"{str(generate_username()[0])}"
            
            elif attribute == 'email':
                if firstname_generated is None:
                    firstname_generated = record.get('firstName', fake.first_name())
                    lastname_generated = record.get('lastName', fake.last_name())
                include_number = np.random.choice([True, False], p=[0.9, 0.1])
                random_number = user_num if include_number else ""
                domain = random.choice(email_domains)

                record[attribute] = f"{firstname_generated.lower()}.{lastname_generated.lower()}{random_number}@{domain}"
            elif attribute == 'password':
                include_number = np.random.choice([True, False], p=[0.1, 0.9])
                if include_number:
                    record[attribute] = "12345678"  
                else:
                    record[attribute] = fake.password()
            elif attribute == 'birthDate':
                start_date = datetime.date(1950, 1, 1)
                end_date = datetime.date(2006, 12, 31)
                random_birthDate = fake.date_between(start_date=start_date, end_date=end_date)
                record[attribute] = str(random_birthDate)
            elif attribute == 'badgeName':
                record[attribute] = fake.word()
            elif attribute == 'badgeDescription':
                record[attribute] = fake.text()
            elif attribute == 'badgeIssuedOn':
                start_date = datetime.date(2000, 1, 1)
                end_date = datetime.date(2023, 12, 31)
                random_issueDate = fake.date_between(start_date=start_date, end_date=end_date)
                record[attribute] = str(random_issueDate)
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
        data.append(record)
        results_times.append(time.time())
    
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
