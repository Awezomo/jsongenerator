import json
import random
import datetime
import time
from faker import Faker

# Initialize the Faker library with German locale settings for Austria and Germany
fake = Faker(['de_AT', 'de_DE'])

# Load the sample data from activities.json
with open('./activities.json', 'r', encoding='utf-8') as file:
    sample_data = json.load(file)

def handle_activities(data=None, attributes=None, num_records=None, action='generate'):
    """
    Handle the generation or anonymization of activity records.

    Args:
        data (list): List of dictionaries containing activity data to be anonymized. Required if action is 'anonymize'.
        attributes (list): List of attributes to either generate or anonymize in the records.
        num_records (int): Number of records to generate. Required if action is 'generate'.
        action (str): Specifies the action to perform - 'generate' to create new records or 'anonymize' to anonymize existing ones.

    Returns:
        tuple: A list of processed records and a list of processing times for each record.
    """
    
    # Validate the action parameter to ensure it is either 'generate' or 'anonymize'
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # If anonymizing, ensure the data is a list of dictionaries
    if action == 'anonymize':
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")

    results_times = []  # List to store the time taken to process each record
    data_to_return = []  # List to store the generated or anonymized records

    if action == 'generate':
        # Loop to generate the specified number of records
        for _ in range(num_records):
            record = {}
            start_date_value = None  # Placeholder for start date to use when generating end dates

            # Generate values for each attribute in the specified list
            for attribute in attributes:
                if attribute == 'title':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("title", fake.catch_phrase())
                elif attribute == 'description':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("description", "")
                elif attribute == 'startdate':
                    sample_record = random.choice(sample_data)
                    start_date_value = sample_record.get("startdate")
                    if start_date_value:
                        # If start date is already in datetime format, format it as a string
                        if isinstance(start_date_value, datetime.datetime):
                            record[attribute] = start_date_value.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            record[attribute] = start_date_value
                    else:
                        # Generate a random start date if one is not available in the sample data
                        start_date_value = fake.date_time_between(start_date='-10y', end_date='now')
                        record[attribute] = start_date_value.strftime('%Y-%m-%d %H:%M:%S')
                elif attribute == 'enddate':
                    if start_date_value:
                        # Generate an end date based on the previously generated start date
                        start_date_dt = datetime.datetime.strptime(start_date_value, '%Y-%m-%d %H:%M:%S')
                        end_date_dt = fake.date_time_between(start_date=start_date_dt)
                        record[attribute] = end_date_dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # Use sample data or generate a random end date if start date is not set
                        sample_record = random.choice(sample_data)
                        end_date_value = sample_record.get("enddate")
                        if end_date_value:
                            if isinstance(end_date_value, datetime.datetime):
                                record[attribute] = end_date_value.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                record[attribute] = end_date_value
                        else:
                            record[attribute] = fake.date_time_between(start_date='now', end_date='-5y').strftime('%Y-%m-%d %H:%M:%S')
                elif attribute == 'geoinfo':
                    # Generate geographical information with name, latitude, and longitude
                    geo_sample_name = random.choice(sample_data)
                    geo_sample_lat = random.choice(sample_data)
                    geo_sample_long = random.choice(sample_data)
                    record[attribute] = {
                        "name": geo_sample_name.get("geoinfo", {}).get("name", fake.city()),
                        "latitude": geo_sample_lat.get("geoinfo", {}).get("latitude", str(fake.latitude())),
                        "longitude": geo_sample_long.get("geoinfo", {}).get("longitude", str(fake.longitude()))
                    }
                # Handle other attributes by either copying from sample data or generating a random value
                elif attribute == 'duration':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("duration", f"{random.randint(1, 8)}")
                elif attribute == 'purpose':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("purpose", "")
                elif attribute == 'role':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("role", "")
                elif attribute == 'rank':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("rank", "")
                elif attribute == 'phase':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("phase", "")
                elif attribute == 'unit':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("unit", "")
                elif attribute == 'level':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("level", "")
                elif attribute == 'tasktype':
                    sample_record = random.choice(sample_data)
                    record[attribute] = random.choice(sample_record.get("tasktype", ""))
                elif attribute == 'bereich':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("bereich", "")
                else:
                    # Generate a random word for any other unspecified attribute
                    record[attribute] = fake.word()
            data_to_return.append(record)  # Add the generated record to the list
            results_times.append(time.time())  # Record the time after processing each record

    elif action == 'anonymize':
        # Loop to anonymize the provided data
        for record in data:
            start_time = time.time()  # Record the start time for processing the record
            new_record = record.copy()  # Create a copy of the original record

            # Anonymize each specified attribute in the record
            for attribute in attributes:
                if attribute in record:  # Only anonymize if the attribute exists in the original record
                    if attribute == 'title':
                        new_record[attribute] = fake.catch_phrase()
                    elif attribute == 'description':
                        new_record[attribute] = fake.text(max_nb_chars=20)
                    elif attribute == 'startDate':
                        start_date_value = fake.date_time_between(start_date='-15y', end_date='now')
                        new_record[attribute] = start_date_value.strftime('%Y-%m-%d %H:%M:%S')
                    elif attribute == 'endDate':
                        if 'startDate' in new_record:
                            start_date_dt = datetime.datetime.strptime(new_record['startDate'], '%Y-%m-%d %H:%M:%S')
                            new_record[attribute] = fake.date_time_between(start_date=start_date_dt, end_date='-1y').strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            new_record[attribute] = fake.date_time_between(start_date='now', end_date='-1y').strftime('%Y-%m-%d %H:%M:%S')
                    elif attribute == 'geoinfo':
                        new_record[attribute] = {
                            "name": fake.city(),
                            "latitude": str(fake.latitude()),
                            "longitude": str(fake.longitude())
                        }
                    elif attribute == 'duration':
                        new_record[attribute] = f"{random.randint(1, 8)}.0"
                    elif attribute == 'purpose':
                        new_record[attribute] = fake.word()
                    elif attribute == 'role':
                        new_record[attribute] = fake.word()
                    elif attribute == 'rank':
                        new_record[attribute] = fake.word()
                    elif attribute == 'phase':
                        new_record[attribute] = fake.word()
                    elif attribute == 'unit':
                        new_record[attribute] = fake.word()
                    elif attribute == 'level':
                        new_record[attribute] = fake.word()
                    elif attribute == 'taskType':
                        new_record[attribute] = fake.word()
                    elif attribute == 'bereich':
                        new_record[attribute] = fake.word()
                    else:
                        new_record[attribute] = fake.word()
            data_to_return.append(new_record)  # Add the anonymized record to the list
            end_time = time.time()  # Record the end time after processing the record
            results_times.append(end_time - start_time)  # Store the processing time for the record
    
    return data_to_return, results_times  # Return the list of processed records and the processing times
