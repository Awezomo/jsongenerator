import datetime
import random
from faker import Faker
import markovify
import random
import time

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

def handle_badges(data=None, attributes=None, num_records=None, action='generate'):
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    if action == 'anonymize':
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")

    results_times = []
    badge_names = ['FuLA Gold', 'FLA Gold', 'FuLA Silber', 'FLA Silber', 'FuLA Bronze', 'FLA Bronze', 'THL Gold', 'THL Silber', 'THL Bronze']

    if action == 'generate':
        data = []

    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]
        start_time = time.time()

        for attribute in attributes:
            if attribute == 'badgeName' or attribute == 'badgeDescription':
                choice = random.choice(badge_names)
                record['badgeName'] = choice
                record['badgeDescription'] = f"{choice} Abzeichen"
            elif attribute == 'badgeIssuedOn':
                start_date = datetime.date(1970, 1, 1)
                end_date = datetime.date(2023, 12, 31)
                record[attribute] = str(fake.date_between(start_date=start_date, end_date=end_date))
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
