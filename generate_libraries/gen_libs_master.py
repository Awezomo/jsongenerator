# Description: This file is the master file for the generation of data for the JSON files. It calls the respective functions from the other files to generate the data for the JSON files.  
from generate_libraries import generate_persons,generate_badges,generate_activities,generate_organisations,generate_goals

def generate_data(jsonType, selected_attributes, uploadedData, num_records=1):
    
    results = []
    print("Uploaded data: ", uploadedData)
    if uploadedData is None:

        if jsonType == 'persons':
            print("Generating persons in person main file")
            generated_data, results_times = generate_persons.generate_json_data(selected_attributes, num_records)
        elif jsonType == 'badges':
            generated_data, results_times = generate_badges(selected_attributes, uploadedData, num_records)
        elif jsonType == 'activities':
            generated_data, results_times = generate_activities(selected_attributes, uploadedData, num_records)
        elif jsonType == 'organisations':
            generated_data, results_times = generate_organisations(selected_attributes, uploadedData, num_records)
        elif jsonType == 'goals':
            generated_data, results_times = generate_goals(selected_attributes, uploadedData, num_records)
        else:
            raise ValueError(f"Invalid JSON type: {jsonType}")
        
        results = generated_data
    else:
        print("Uploaded data found")
        results = generate_persons.generate_data_mf(uploadedData, num_records)

    if results:
        return results, results_times
    else:
        return {}
    