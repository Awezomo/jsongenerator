import datetime
import random
import time
from faker import Faker
import numpy as np

# Initialize Faker with a German locale
fake = Faker(['de_AT'])

def handle_organisations(data=None, attributes=None, num_records=None, action='generate'):
    """
    Generate or anonymize organisation data based on the provided action and attributes.

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
    
    results_times = []  # List to store the time taken to process each record

    if action == 'generate':
        data = []  # Initialize an empty list if generating new data
    
    # Define a dictionary for organization names and their abbreviations
    organisations = {
        'Rotes Kreuz': 'RK', 'Caritas': 'C', 'Diakonie': 'D', 'Volkshilfe': 'VH', 
        'Arbeiter Samariter Bund': 'ASB', 'Malteser': 'M', 'Johanniter': 'J', 
        'Pfarrcaritas': 'PC', 'Feuerwehr': 'FF', 'Polizei': 'P'
    }
    
    # Define a list of tags for organizations
    tags = [
        "Gemeinschaftsdienst", "Nachbarschaftshilfe", "Umweltschutz", "Bildungsförderung",
        "Soziale Gerechtigkeit", "Jugendarbeit", "Seniorenbetreuung", "Integration",
        "Flüchtlingshilfe", "Katastrophenschutz", "Gesundheitsförderung", "Kulturförderung",
        "Sportförderung", "Tierschutz", "Menschenrechte", "Obdachlosenhilfe", "Frauenförderung",
        "Kinderbetreuung", "Inklusion", "Bildungschancen", "Entwicklungshilfe", "Berufsbildung",
        "Krisenintervention", "Seelsorge", "Freiwilligendienst"
    ]

    # Generate or anonymize records based on the provided attributes
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]  # Use existing data for anonymization
        
        start_time = time.time()  # Start timing the record processing

        print(attributes)  # Print the attributes for debugging

        for attribute in attributes:
            if attribute == 'organisationName':
                # Randomly select an organization name
                org_name = random.choice(list(organisations.keys()))
                record[attribute] = org_name
            elif attribute == 'abbreviation':
                # Retrieve the abbreviation based on the organization name
                org_name = record.get('organisationName')
                record[attribute] = organisations.get(org_name, '')
            elif attribute == 'orgDescription':
                # Create a description for the organization
                record[attribute] = f"Organisation {record['organisationName']}, abgekürzt mit {record['abbreviation']}"
            elif attribute == 'orgWebsite':
                # Generate a website URL, or use a fake URL if anonymizing
                if action == 'anonymize':
                    record[attribute] = fake.url()
                else:
                    record[attribute] = f"https://{record['organisationName'].lower()}.at/"
            elif attribute == 'orgImage':
                # Generate a fake image URL
                record[attribute] = fake.image_url()
            elif attribute == 'orgTags':
                # Randomly select 1 to 3 tags from the list
                selected_tags = random.sample(tags, random.randint(1, 3))
                record[attribute] = ", ".join(selected_tags)
            elif attribute == 'orgLocation':
                # Generate a fake city name
                record[attribute] = fake.city()
            else:
                # Generate a fake word for any other attributes
                record[attribute] = fake.word()
        
        end_time = time.time()  # End timing the record processing
        results_times.append(end_time - start_time)  # Record the time taken

        if action == 'generate':
            data.append(record)  # Append the new record to the data list
    
    return data, results_times  # Return the processed data and the times taken
