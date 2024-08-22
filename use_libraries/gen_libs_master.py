# Description: This file serves as the master controller for generating data for JSON files.
# It calls the respective functions from other modules to handle the data generation or modification process.

from use_libraries import activities, badges, goals, organisations, persons

def generate_data(jsonType, selected_attributes, uploadedData, num_records=1):
    """
    Generate or modify data based on the provided JSON type and attributes.

    Args:
        jsonType (str): The type of JSON data to handle (e.g., 'persons', 'badges').
        selected_attributes (list): Attributes to be included in the generated data.
        uploadedData (list): Existing data that might be used for modification.
        num_records (int): The number of records to generate (if generating new data).

    Returns:
        tuple: A tuple containing the generated or modified data and the times taken to process each record.
               If no results are generated, an empty dictionary is returned.
    """

    results = []
    print("Uploaded data: ", uploadedData)  # Debugging output to display the uploaded data

    if uploadedData is None:
        # If no uploaded data is provided, generate new data based on the JSON type
        if jsonType == 'persons':
            generated_data, results_times = persons.handle_persons(attributes=selected_attributes, num_records=num_records, action="generate")
        elif jsonType == 'badges':
            generated_data, results_times = badges.handle_badges(attributes=selected_attributes, num_records=num_records, action="generate")
        elif jsonType == 'activities':
            generated_data, results_times = activities.handle_activities(attributes=selected_attributes, num_records=num_records, action="generate")
        elif jsonType == 'organisations':
            generated_data, results_times = organisations.handle_organisations(attributes=selected_attributes, num_records=num_records, action="generate")
        elif jsonType == 'goals':
            generated_data, results_times = goals.handle_goals(attributes=selected_attributes, num_records=num_records, action="generate")
        else:
            # Raise an error if an invalid JSON type is provided
            raise ValueError(f"Invalid JSON type: {jsonType}")
        
        results = generated_data  # Store the generated data in the results variable
    else:
        print("Uploaded data found")  # Debugging output indicating that uploaded data is found
        results = persons.generate_data_mf(uploadedData, num_records)  # Modify the existing data using Markov models

    if results:
        return results, results_times  # Return the generated/modified data and the processing times
    else:
        return {}  # Return an empty dictionary if no results are generated
