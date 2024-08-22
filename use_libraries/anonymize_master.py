# Import anonymization handling functions from the respective modules
from use_libraries import persons, badges, activities, organisations, goals

def anonymize_data(uploaded_data, selected_attributes, method, json_type):
    """
    Anonymize data based on the selected method and type of JSON data.

    Args:
        uploaded_data (list): The data to be anonymized, provided as a list of dictionaries.
        selected_attributes (list): List of attributes to be anonymized within the uploaded data.
        method (str): The method used for anonymization, e.g., "Python Libraries" or "Large Language Model".
        json_type (str): The type of data to be anonymized, which can be "persons", "badges", "activities", "organisations", or "goals".

    Returns:
        anonymized_data: The anonymized data, which will be structured similarly to the input data.
    """

    anonymized_data = None  # Initialize the variable to store the anonymized data

    # Anonymization using Python Libraries
    if method == "Python Libraries":
        # Determine the type of JSON data and apply the corresponding anonymization function
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

    return anonymized_data  # Return the anonymized data

