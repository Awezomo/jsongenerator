from generate_llm import llm_activities, llm_badges, llm_goals, llm_organisations, llm_persons

result_times = []
valid_result = []

def generate_data(jsonType, uploadedData, num_records):

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
        return []
