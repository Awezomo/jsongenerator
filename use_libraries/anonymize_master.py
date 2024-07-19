# use_libraries/anonymize_master.py

from use_libraries import persons, badges, activities, organisations, goals

def anonymize_data(uploaded_data, selected_attributes, method, json_type):
    anonymized_data = None

    if method == "Python Libraries":
        if json_type == "persons":
            anonymized_data = persons.handle_persons(uploaded_data, selected_attributes, action="anonymize")
        elif json_type == "badges":
            anonymized_data = badges.handle_badges(uploaded_data, selected_attributes, action="anonymize")
        elif json_type == "activities":
            anonymized_data = activities.handle_activities(uploaded_data, selected_attributes, action="anonymize")
        elif json_type == "organisations":
            anonymized_data = organisations.handle_organisations(uploaded_data, selected_attributes, action="anonymize")
        elif json_type == "goals":
            anonymized_data = goals.handle_goals(uploaded_data, selected_attributes, action="anonymize")
    elif method == "Large Language Model":
        # Implement LLM anonymization logic here if necessary
        pass

    return anonymized_data
