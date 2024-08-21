from generate_llm import llm_activities, llm_badges, llm_goals, llm_organisations, llm_persons

def anonymize_data(uploaded_data, selected_attributes, json_type):
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
        return []