from generate_llm import llm_activities, llm_badges, llm_goals, llm_organisations, llm_persons

# Global lists to store result times and valid results (initially empty)
result_times = []
valid_result = []

def generate_data(jsonType, uploadedData, num_records):
    """
    Generate data based on the provided JSON type and number of records using LLM functions.

    Args:
        jsonType (str): Type of JSON data to generate ('persons', 'badges', 'activities', 'organisations', 'goals').
        uploadedData (list): Data to use for generation (not used in current implementation).
        num_records (int): Number of records to generate.

    Returns:
        list: Generated data based on the specified JSON type, or an empty list if jsonType is invalid.
    """
    
    # Call the appropriate LLM generation function based on the jsonType
    if jsonType == 'persons':
        return llm_persons.generate_persons(num_records)
    elif jsonType == 'badges':
        return llm_badges.generate_badges(num_records)
    elif jsonType == 'activities':
        return llm_activities.generate_activities(num_records)
    elif jsonType == 'organisations':
        return llm_organisations.generate_organisations(num_records)
    elif jsonType == 'goals':
        return llm_goals.generate_goals(num_records)
    else:
        # Return an empty list if jsonType is invalid
        return []
