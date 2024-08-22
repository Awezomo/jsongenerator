import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for
import json
from io import BytesIO
import matplotlib

# Custom modules for data generation and anonymization
import generate_llm.anonymize_master
import use_libraries.anonymize_master
import use_libraries.gen_libs_master

# Use the Agg backend for Matplotlib (suitable for web applications)
matplotlib.use('agg')
import time

import generate_llm.gen_llm
from visualize import visualize_data  # Import the visualize_data function

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure JSON responses are not ASCII encoded

# Global variables for storing data across requests
saved_json_data = None
json_data = None
json_type = None
method = None
visualization_html = None
time_metrics = None

def generate_data(jsonType, uploadedData, attributes, method, num_records):
    """
    Generate synthetic JSON data based on the selected method and attributes.

    Args:
        jsonType (str): The type of JSON being generated.
        uploadedData (dict): The uploaded JSON data for reference (if any).
        attributes (list): The list of attributes to include in the generated data.
        method (str): The method used for data generation ('Python Libraries' or 'Large Language Model').
        num_records (int): The number of records to generate.

    Returns:
        list: The generated JSON data.
    """
    global time_metrics

    results_validity = []
    results_times = []
    start_time = time.time()
    data = []

    # Generate data using Python libraries
    if method == 'Python Libraries':
        print("Generating data using Python libraries")
        data, results_times = use_libraries.gen_libs_master.generate_data(jsonType, attributes, uploadedData, num_records)
    
    # Generate data using a Large Language Model (LLM)
    if method == 'Large Language Model':
        print("Generating data using LLM")
        print("Attributes: ", attributes)
        data, results_times, results_validity = generate_llm.gen_llm.generate_data(jsonType, uploadedData, num_records)
        # Filter data to include only the selected attributes
        data = [{attr: entry[attr] for attr in attributes} for entry in data]

    end_time = time.time()
    generation_time = end_time - start_time
    generation_time = round(generation_time, 4)
    avg_time_per_record = generation_time / num_records if num_records > 0 else 0
    results_times = [round(entry - start_time, 2) for entry in results_times]
    results_times.insert(0, 0)  # Insert the start time as the first entry

    # Store timing metrics for the generation process
    time_metrics = {
        'generation_time': generation_time,
        'avg_time_per_record': avg_time_per_record,
        'results_times': results_times,
        'result_validity': results_validity if results_validity else None
    }
    return data

@app.route('/')
def index():
    """
    Render the home page.
    """
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    """
    Redirect to the favicon.ico file.
    """
    return redirect(url_for('static', filename='favicon.ico'), code=301)


@app.route('/<json_type>')
def json_type(json_type):
    """
    Render a page corresponding to the specified JSON type.
    
    Args:
        json_type (str): The type of JSON.

    Returns:
        str: The rendered template for the specified JSON type.
    """
    return render_template('{}.html'.format(json_type))


def preprocess_json(json_data):
    """
    Preprocess JSON data to remove line breaks within string values.

    Args:
        json_data (str): The raw JSON data as a string.

    Returns:
        str: The preprocessed JSON data.
    """
    return json_data.replace('\n', ' ').replace('\r', '')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Handle the generation of synthetic JSON data based on user input.
    
    Returns:
        str: The rendered template with the generated JSON data and visualizations.
    """
    global json_data, json_type, visualization_html, saved_json_data, method, time_metrics

    # Get parameters from the form submission
    json_type = request.form['jsonType']
    selected_attributes = request.form.getlist('attribute')
    method = request.form['method']
    uploaded_file = request.files['file']
    num_records = int(request.form.get('numRecords', 1))

    # Check if a file was uploaded
    if uploaded_file.filename != '':
        # Read and preprocess the uploaded file's contents
        file_contents = uploaded_file.read().decode('utf-8')
        file_contents = preprocess_json(file_contents)
        
        # Parse the file contents as JSON data
        try:
            uploaded_data = json.loads(file_contents)
        except json.JSONDecodeError as e:
            return jsonify({'error': 'Invalid JSON file'}), 400
    else:
        uploaded_data = None

    # Generate the synthetic JSON data
    data = generate_data(json_type, uploaded_data, selected_attributes, method, num_records)

    # Convert the generated data to a formatted JSON string
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)

    # Generate visualizations based on the timing metrics
    visualization_html = visualize_data(time_metrics, saved_json_data, method, json_type)

    # Render the results template with the generated data and visualizations
    return render_template('results.html', json_data=json_data, json_type=json_type, visualization_html=visualization_html, saved_json_data=saved_json_data, generation_method=method)

@app.route('/anonymize', methods=['POST'])
def anonymize():
    """
    Handle the anonymization of JSON data based on user input.

    Returns:
        str: The rendered template with the original and anonymized JSON data.
    """
    global json_data, json_type, uploaded_data

    # Get parameters from the form submission
    json_type = request.form['jsonType']
    selected_attributes = request.form.getlist('attribute')
    uploaded_file = request.files['file']
    method = request.form['method']

    # Check if a file was uploaded
    if uploaded_file.filename != '':
        # Read and preprocess the uploaded file's contents
        file_contents = uploaded_file.read().decode('utf-8')
        file_contents = preprocess_json(file_contents)
        
        # Parse the file contents as JSON data
        try:
            uploaded_data = json.loads(file_contents)
        except json.JSONDecodeError as e:
            return jsonify({'error': 'Invalid JSON file'}), 400
    else:
        uploaded_data = None

    if uploaded_data is None:
        return jsonify({'error': 'Upload Error: No JSON data provided'}), 400

    # Store the original JSON data for display
    original_json_data = json.dumps(uploaded_data, indent=4, ensure_ascii=False)
    
    # Anonymize the data using the selected method
    if method == "Python Libraries":
        anonymized_data, _ = use_libraries.anonymize_master.anonymize_data(uploaded_data, selected_attributes, method, json_type)
    elif method == "Large Language Model":
        anonymized_data = generate_llm.anonymize_master.anonymize_data(uploaded_data, selected_attributes, json_type)
    else:
        anonymized_data = ["No valid method provided"]

    # Convert the anonymized data to a formatted JSON string
    json_data = json.dumps(anonymized_data, indent=4, ensure_ascii=False)

    # Render the results template with the original and anonymized data
    return render_template('anonymize_results.html', 
                           original_json_data=original_json_data, 
                           anonymized_json_data=json_data, 
                           json_type=json_type,
                           method=method, 
                           selected_attributes=selected_attributes)

@app.route('/download_json', methods=['POST'])
def download_json():
    """
    Handle the download of generated or anonymized JSON data.

    Returns:
        Response: The JSON data as an attachment for download.
    """
    json_data = request.form.get('json_data')
    json_type = request.form.get('json_type')

    if json_data is None:
        abort(400, "No JSON data provided")

    # Create a BytesIO stream to hold the JSON data
    fake_file = BytesIO(json_data.encode())
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{json_type}_{current_datetime}.json"

    # Send the file as a download
    return send_file(fake_file, as_attachment=True, download_name=file_name)


@app.route('/save_json', methods=['POST'])
def save_json():
    """
    Save the generated JSON data and associated metadata for later comparison.

    Returns:
        Redirect: Redirects to the home page.
    """
    global saved_json_data, json_type, method, time_metrics

    # Save the current JSON data and associated metrics
    saved_json_data = {
        'json_data': request.form['json_data'],
        'json_type': json_type,
        'generation_method': method,
        'generation_time': time_metrics['generation_time'],
        'avg_time_per_record': time_metrics['avg_time_per_record'],
        'results_times': time_metrics['results_times'],
        'result_validity': time_metrics['result_validity']
    }
    return redirect(url_for('index'))


@app.route('/clear_comparison', methods=['POST'])
def clear_comparison():
    """
    Clear the saved comparison data and refresh the results page.

    Returns:
        str: The rendered template with updated data.
    """
    global saved_json_data, visualization_html
    saved_json_data = None  # Clear the saved comparison data
    
    # Recompute the visualization HTML without the saved JSON data
    visualization_html = visualize_data(time_metrics, saved_json_data, method, json_type)
    
    # Return the results template with updated data
    return render_template('results.html', json_data=json_data, json_type=json_type, visualization_html=visualization_html, saved_json_data=saved_json_data, generation_method=method)


if __name__ == '__main__':
    app.run(debug=True)
