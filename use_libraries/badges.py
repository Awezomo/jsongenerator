import datetime
import random
from faker import Faker
import markovify
import time

# Initialize Faker with German locales
fake = Faker(['de_AT', 'de_DE'])

def handle_badges(data=None, attributes=None, num_records=None, action='generate'):
    """
    Handle badge data either by generating new records or anonymizing existing ones.

    Args:
        data (list): Existing data to be anonymized or extended with generated records.
        attributes (list): List of attributes to be handled in each record (e.g., 'badgeName', 'badgeIssuedOn').
        num_records (int): Number of records to generate. Used only in 'generate' mode.
        action (str): Specifies whether to 'generate' new records or 'anonymize' existing ones.

    Returns:
        tuple: A list of handled records and a list of times taken to process each record.
    """
    
    # Ensure the action is valid
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # Check that data is a list of dictionaries when anonymizing
    if action == 'anonymize':
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")
    
    results_times = []  # List to store the time taken to process each record
    badge_names = ['FuLA Gold', 'FLA Gold', 'FuLA Silber', 'FLA Silber', 'FuLA Bronze', 'FLA Bronze', 'THL Gold', 'THL Silber', 'THL Bronze']

    # Initialize an empty list for data generation
    if action == 'generate':
        data = []

    # Loop over the number of records to handle
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]  # Use existing record if anonymizing

        start_time = time.time()  # Record start time for processing

        # Handle each attribute in the record
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
                record[attribute] = fake.word()  # Generate a random word for other attributes

        end_time = time.time()  # Record end time for processing
        results_times.append(end_time - start_time)  # Calculate and store processing time

        if action == 'generate':
            data.append(record)  # Append the generated record to data

    return data, results_times  # Return the processed data and timing information

def train_markov_model(uploaded_data, attribute):
    """
    Train a Markov model on the specified attribute from the uploaded data.

    Args:
        uploaded_data (list): List of records to train the model on.
        attribute (str): The attribute to use for training the Markov model.

    Returns:
        markovify.Text or None: Trained Markov model or None if no valid text is found.
    """
    
    if uploaded_data is None:
        return None
    
    text = ""
    for data in uploaded_data:
        if attribute in data:
            text += data[attribute] + " "  # Concatenate text from the specified attribute

    if not text:
        return None
    
    return markovify.Text(text)  # Return the trained Markov model

def extract_attributes(uploaded_data):
    """
    Extract a list of attribute names from the first record in the uploaded data.

    Args:
        uploaded_data (list): List of records from which to extract attributes.

    Returns:
        list: List of attribute names.
    """
    
    attributes = []
    if uploaded_data:
        attributes = list(uploaded_data[0].keys())  # Get the keys (attribute names) from the first record
    return attributes

def generate_data_mf(uploaded_data, num_records=1):
    """
    Generate new records using Markov models trained on the uploaded data.

    Args:
        uploaded_data (list): List of records to base the generation on.
        num_records (int): Number of records to generate.

    Returns:
        list: List of generated records.
    """
    
    if not uploaded_data:
        return None

    attributes = extract_attributes(uploaded_data)  # Extract attribute names from the uploaded data
    results = []
    selected_badges = set()  # Track badge names to avoid duplicates

    while len(results) < num_records:
        selected_record = random.choice(uploaded_data)  # Randomly select a record to base the generation on
        badge_name = selected_record['badgeName']

        if badge_name not in selected_badges:
            result = {}

            for attribute in attributes:
                model = train_markov_model([selected_record], attribute)
                if model is not None:
                    generated_word = model.make_sentence(tries=100, test_output=False).strip()
                    if generated_word is None:
                        generated_word = fake.word()  # Fallback to a random word if Markov generation fails
                else:
                    generated_word = fake.word()  # Fallback to a random word if no model is generated

                # Add the generated word to the result
                result[attribute] = generated_word

            results.append(result)  # Add the generated record to the results
            selected_badges.add(badge_name)  # Mark the badge name as used

    return results  # Return the generated records
