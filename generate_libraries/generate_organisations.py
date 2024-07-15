import datetime
import random
from faker import Faker
import markovify
import random

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

# Function to generate structured data using Faker
def generate_json_data(attributes, num_records):

    data = []
    org = None

    for _ in range(num_records):
        record = {}
        for attribute in attributes:
            if attribute == 'organisationName' or attribute == 'abbreviation': 
                organisations = {'Rotes Kreuz': 'RK', 'Caritas': 'C', 'Diakonie': 'D', 'Volkshilfe': 'VH', 'Arbeiter Samariter Bund': 'ASB', 'Malteser': 'M', 'Johanniter': 'J', 'Pfarrcaritas': 'PC', 'Feuerwehr': 'FF', 'Polizei': 'P'}
                org = random.choice(organisations)
                record['organisationName'] = org.key()
                record['abbreviation'] = org.value()
            elif attribute == 'abbreviation':
                continue
            elif attribute == 'orgDescription':
                pass
            elif attribute == 'orgWebsite':
                record[attribute] = fake.word()
            elif attribute == 'orgImage':
                record[attribute] = fake.word()
            elif attribute == 'orgTags':
                record[attribute] = fake.word()
            elif attribute == 'orgLocation':
                record[attribute] = fake.word()
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
