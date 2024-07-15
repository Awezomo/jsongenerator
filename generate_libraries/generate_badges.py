import datetime
import random
from faker import Faker
import markovify
import random

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

# Function to generate structured data using Faker
def generate_json_data(attributes, num_records=10):

    data = []
    for _ in range(num_records):
        record = {}
        for attribute in attributes:
            if attribute == 'badgeName' or attribute == 'badgeDescription':
                names = ['FuLA Gold', 'FLA Gold', 'FuLA Silber', 'FLA Silber', 'FuLA Bronze', 'FLA Bronze', 'THL Gold', 'THL Silber', 'THL Bronze']
                record[attribute] = random.choice(names) 
                record['badgeDescription'] = random.choice(names) 
            elif attribute == 'badgeIssuedOn':
                start_date = datetime.date(1970, 1, 1)
                end_date = datetime.date(2023, 12, 31)
                random_birthDate = fake.date_between(start_date=start_date, end_date=end_date)
                record[attribute] = str(random_birthDate)
            else:
                record[attribute] = fake.word()
        
        data.append(record)
    
    return data

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
