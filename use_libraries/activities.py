import json
import random
import datetime
import time
from faker import Faker

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

# Load the sample data from activities.json
with open('./activities.json', 'r', encoding='utf-8') as file:
    sample_data = json.load(file)

def handle_activities(data=None, attributes=None, num_records=None, action='generate'):
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    if action == 'anonymize':
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")

    results_times = []
    data_to_return = []

    if action == 'generate':
        for _ in range(num_records):
            record = {}
            start_date_value = None

            for attribute in attributes:
                if attribute == 'title':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("title", fake.catch_phrase())
                elif attribute == 'description':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("description", "")
                elif attribute == 'startDate':
                    sample_record = random.choice(sample_data)
                    start_date_value = sample_record.get("startdate")
                    if start_date_value:
                        if isinstance(start_date_value, datetime.datetime):
                            record[attribute] = start_date_value.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            record[attribute] = start_date_value
                    else:
                        start_date_value = fake.date_time_between(start_date='-10y', end_date='now')
                        record[attribute] = start_date_value.strftime('%Y-%m-%d %H:%M:%S')
                elif attribute == 'endDate':
                    if start_date_value:
                        start_date_dt = datetime.datetime.strptime(start_date_value, '%Y-%m-%d %H:%M:%S')
                        end_date_dt = fake.date_time_between(start_date=start_date_dt)
                        record[attribute] = end_date_dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
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
                    geo_sample_name = random.choice(sample_data)
                    geo_sample_lat = random.choice(sample_data)
                    geo_sample_long = random.choice(sample_data)
                    record[attribute] = {
                        "name": geo_sample_name.get("geoinfo", {}).get("name", fake.city()),
                        "latitude": geo_sample_lat.get("geoinfo", {}).get("latitude", str(fake.latitude())),
                        "longitude": geo_sample_long.get("geoinfo", {}).get("longitude", str(fake.longitude()))
                    }
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
                elif attribute == 'taskType':
                    sample_record = random.choice(sample_data)
                    record[attribute] = random.choice(sample_record.get("tasktype", ""))
                elif attribute == 'bereich':
                    sample_record = random.choice(sample_data)
                    record[attribute] = sample_record.get("bereich", "")
                else:
                    record[attribute] = fake.word()
            data_to_return.append(record)
            results_times.append(time.time())

    elif action == 'anonymize':
        for record in data:
            start_time = time.time()
            new_record = record.copy()  # Copy the original record

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
            data_to_return.append(new_record)
            end_time = time.time()
            results_times.append(end_time - start_time)
    
    return data_to_return, results_times
