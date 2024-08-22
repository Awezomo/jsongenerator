import datetime
import random
import time
from faker import Faker
from random_username.generate import generate_username

import numpy as np
import random

# Initialize Faker with German locale
fake = Faker(['de_AT', 'de_DE'])

def handle_persons(data=None, attributes=None, num_records=None, action='generate'):
    """
    Generate or anonymize person data based on the provided action and attributes.

    Args:
        data (list, optional): Existing data to be anonymized. Should be a list of dictionaries.
        attributes (list): List of attributes to be included in the data.
        num_records (int, optional): Number of records to generate if action is 'generate'.
        action (str): Action to perform, either 'generate' for creating new data or 'anonymize' for modifying existing data.

    Returns:
        tuple: A tuple containing the processed data and the time taken for each record.
    """
    
    # Validate the action parameter
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # Process the data if the action is 'anonymize'
    if action == 'anonymize':
        if isinstance(data, list) and isinstance(data[0], list):
            data = data[0]  # Flatten the nested list if necessary
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")
    
    firstname_generated = None
    lastname_generated = None
    user_num = fake.random_int(min=1, max=9999)
    email_domains = ['gmail.com', 'aon.at', 'gmx.at', 'outlook.com']
    results_times = []  # List to store the time taken to process each record

    if action == 'generate':
        data = []  # Initialize an empty list if generating new data
    
    # Generate or anonymize records based on the provided attributes
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]  # Use existing data for anonymization
        
        start_time = time.time()  # Start timing the record processing

        for attribute in attributes:
            if attribute == 'firstName':
                if not firstname_generated:
                    firstname_generated = fake.first_name()  # Generate first name if not already done
                record[attribute] = firstname_generated
            elif attribute == 'lastName':
                if not lastname_generated:
                    lastname_generated = fake.last_name()  # Generate last name if not already done
                record[attribute] = lastname_generated
            elif attribute == 'userName':
                # Decide if a random number should be included in the username
                include_number = np.random.choice([True, False], p=[0.7, 0.3])
                random_number = user_num if include_number else ""
                # Use generated names or create new ones
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
                # Decide if a random number should be included in the email
                include_number = np.random.choice([True, False], p=[0.9, 0.1])
                random_number = user_num if include_number else ""
                domain = random.choice(email_domains)
                record[attribute] = f"{first_name.lower()}.{last_name.lower()}{random_number}@{domain}"
            elif attribute == 'password':
                # Decide if a fixed or random password should be used
                include_number = np.random.choice([True, False], p=[0.1, 0.9])
                record[attribute] = "12345678" if include_number else fake.password()
            elif attribute == 'birthDate':
                # Generate a random date of birth within a specific range
                start_date = datetime.date(1950, 1, 1)
                end_date = datetime.date(2006, 12, 31)
                record[attribute] = str(fake.date_between(start_date=start_date, end_date=end_date))
            elif attribute == 'badgeName':
                record[attribute] = fake.word()
            elif attribute == 'badgeDescription':
                record[attribute] = fake.text()
            elif attribute == 'badgeIssuedOn':
                # Generate a random date when the badge was issued
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
        
        end_time = time.time()  # End timing the record processing
        results_times.append(end_time - start_time)  # Record the time taken

        if action == 'generate':
            data.append(record)  # Append the new record to the data list
    
    return data, results_times  # Return the processed data and the times taken
