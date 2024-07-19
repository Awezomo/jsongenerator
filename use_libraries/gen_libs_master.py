# Description: This file is the master file for the generation of data for the JSON files. It calls the respective functions from the other files to generate the data for the JSON files.  
from use_libraries import activities, badges, goals, organisations, persons

def generate_data(jsonType, selected_attributes, uploadedData, num_records=1):
    
    results = []
    print("Uploaded data: ", uploadedData)
    if uploadedData is None:

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
            raise ValueError(f"Invalid JSON type: {jsonType}")
        
        results = generated_data
    else:
        print("Uploaded data found")
        results = persons.generate_data_mf(uploadedData, num_records)

    if results:
        return results, results_times
    else:
        return {}
    