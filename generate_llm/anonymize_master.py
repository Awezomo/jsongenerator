from generate_llm import llm_activities, llm_badges, llm_goals, llm_organisations, llm_persons

def anonymize_data(uploaded_data, selected_attributes, json_type):
    """
    Anonymize data based on the provided JSON type and selected attributes using LLM functions.

    Args:
        uploaded_data (list): Data to be anonymized. Should be a list of dictionaries.
        selected_attributes (list): List of attributes to be anonymized.
        json_type (str): Type of JSON data ('persons', 'badges', 'activities', 'organisations', 'goals').

    Returns:
        list: Anonymized data based on the specified JSON type, or an empty list if json_type is invalid.
    """
    
    # Call the appropriate LLM anonymization function based on the json_type
    if json_type == 'persons':
        return llm_persons.anonymize_persons(uploaded_data, selected_attributes)
    elif json_type == 'badges':
        return llm_badges.anonymize_badges(uploaded_data, selected_attributes)
    elif json_type == 'activities':
        return llm_activities.anonymize_activities(uploaded_data, selected_attributes)
    elif json_type == 'organisations':
        return llm_organisations.anonymize_organisations(uploaded_data, selected_attributes)
    elif json_type == 'goals':
        return llm_goals.anonymize_goals(uploaded_data, selected_attributes)
    else:
        # Return an empty list if json_type is invalid
        return []
