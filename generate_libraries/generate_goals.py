import datetime
import random
from faker import Faker
import markovify
import random

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

# Function to generate structured data using Faker
def generate_json_data(attributes, num_records):

    print("Attributes: ", attributes)
    data = []
    for _ in range(num_records):
        record = {}
        for attribute in attributes:
            if attribute == 'type': 
                record[attribute] = fake.word()
            elif attribute == 'level':
                record[attribute] = fake.word()
            elif attribute == 'description':
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

    while len(results) < num_records:
        selected_record = random.choice(uploaded_data)

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

    return results
