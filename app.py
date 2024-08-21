import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for
import json
from io import BytesIO
import matplotlib

import generate_llm.anonymize_master
import use_libraries.anonymize_master
import use_libraries.gen_libs_master
# Use the Agg backend
matplotlib.use('agg')
import time

import generate_llm
from visualize import visualize_data  # Import the visualize_data function

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# Global variable to store the saved JSON data
saved_json_data = None
json_data = None
json_type = None
method = None
visualization_html = None
time_metrics = None


def generate_data(jsonType, uploadedData, attributes, method, num_records):
    global time_metrics

    results_validity = []
    results_times = []
    start_time = time.time()
    results_times = []
    data = []

    if method == 'Python Libraries':
        print("Generating data using Python libraries")
        data, results_times = use_libraries.gen_libs_master.generate_data(jsonType, attributes, uploadedData, num_records)
    
    if method == 'Large Language Model':
        print("Generating data using LLM")
        print("Attributes: ", attributes)
        data, results_times, results_validity = generate_llm.gen_llm.generate_data(jsonType, uploadedData, num_records)
        data = [{attr: entry[attr] for attr in attributes} for entry in data]

    end_time = time.time()
    generation_time = end_time - start_time
    generation_time = round(generation_time, 4)
    avg_time_per_record = generation_time / num_records if num_records > 0 else 0
    results_times = [round(entry - start_time, 2) for entry in results_times]
    results_times.insert(0, 0)

    time_metrics = {
        'generation_time': generation_time,
        'avg_time_per_record': avg_time_per_record,
        'results_times': results_times,
        'result_validity': results_validity if results_validity else None
    }
    return data

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=301)


@app.route('/<json_type>')
def json_type(json_type):
    return render_template('{}.html'.format(json_type))


def preprocess_json(json_data):
    # Remove line breaks within string values
    json_data = json_data.replace('\n', ' ').replace('\r', '')
    return json_data


@app.route('/generate', methods=['POST'])
def generate():
    global json_data, json_type, visualization_html, saved_json_data, method, generation_time, avg_time_per_record

    # Get JSON type, attributes, and generation method from the form
    json_type = request.form['jsonType']
    selected_attributes = request.form.getlist('attribute')
    method = request.form['method']
    uploaded_file = request.files['file']  # Access the uploaded file
    num_records = int(request.form.get('numRecords', 1))

    # Check if a file was uploaded
    if uploaded_file.filename != '':
        # Read the contents of the uploaded file
        file_contents = uploaded_file.read().decode('utf-8')  # Decode bytes to string
        # Preprocess the file contents
        file_contents = preprocess_json(file_contents)
        # Process the file_contents as needed
        # For example, you can parse the contents as JSON data
        try:
            uploaded_data = json.loads(file_contents)
            # Process the uploaded data as needed
        except json.JSONDecodeError as e:
            # Handle JSON decoding error
            return jsonify({'error': 'Invalid JSON file'}), 400
    else:
        uploaded_data = None

    # Generate JSON data based on selected attributes and method
    data = generate_data(json_type, uploaded_data, selected_attributes, method, num_records)

    # Convert data to JSON format
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)
    visualization_html = visualize_data(time_metrics, saved_json_data, method, json_type)

    return render_template('results.html', json_data=json_data, json_type=json_type, visualization_html=visualization_html, saved_json_data=saved_json_data, generation_method=method)

@app.route('/anonymize', methods=['POST'])
def anonymize():
    global json_data, json_type, uploaded_data

    json_type = request.form['jsonType']
    selected_attributes = request.form.getlist('attribute')
    uploaded_file = request.files['file']
    method = request.form['method']

    if uploaded_file.filename != '':
        file_contents = uploaded_file.read().decode('utf-8')
        file_contents = preprocess_json(file_contents)
        try:
            uploaded_data = json.loads(file_contents)
        except json.JSONDecodeError as e:
            return jsonify({'error': 'Invalid JSON file'}), 400
    else:
        uploaded_data = None

    if uploaded_data is None:
        return jsonify({'error': 'Upload Error: No JSON data provided'}), 400

    original_json_data = json.dumps(uploaded_data, indent=4, ensure_ascii=False)
    
    if method=="Python Libraries":
        anonymized_data, _ = use_libraries.anonymize_master.anonymize_data(uploaded_data, selected_attributes, method, json_type)
    elif method=="Large Language Model":
        anonymized_data = generate_llm.anonymize_master.anonymize_data(uploaded_data, selected_attributes, json_type)
    else:
        anonymized_data = ["No valid method provided"]

    json_data = json.dumps(anonymized_data, indent=4, ensure_ascii=False)

    return render_template('anonymize_results.html', 
                           original_json_data=original_json_data, 
                           anonymized_json_data=json_data, 
                           json_type=json_type, 
                           selected_attributes=selected_attributes)

@app.route('/download_json', methods=['POST'])
def download_json():
    json_data = request.form.get('json_data')
    json_type = request.form.get('json_type')

    if json_data is None:
        abort(400, "No JSON data provided")

    fake_file = BytesIO(json_data.encode())
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{json_type}_{current_datetime}.json"

    return send_file(fake_file, as_attachment=True, download_name=file_name)


@app.route('/save_json', methods=['POST'])
def save_json():
    global saved_json_data, json_type, method, time_metrics

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
    global saved_json_data, visualization_html
    saved_json_data = None  # Clear the saved comparison data
    # Recompute the visualization HTML without the saved JSON data
    visualization_html = visualize_data(time_metrics, saved_json_data, method, json_type)
    # Return the results template with updated data
    return render_template('results.html', json_data=json_data, json_type=json_type, visualization_html=visualization_html, saved_json_data=saved_json_data, generation_method=method)


if __name__ == '__main__':
    app.run(debug=True)
