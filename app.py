import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for
import json
from io import BytesIO
import matplotlib
# Use the Agg backend
matplotlib.use('agg')
import time

import generate_libraries.gen_libs_master as gen_libs_master
import generate_llm.gen_llm as gen_llm
from visualize import visualize_data  # Import the visualize_data function

app = Flask(__name__)

# Global variable to store the saved JSON data
saved_json_data = None
json_data = None
json_type = None
generation_method = None
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
        data, results_times = gen_libs_master.generate_data(jsonType, attributes, uploadedData, num_records)
    
    if method == 'Large Language Model':
        print("Generating data using LLM")
        data, results_times, results_validity = gen_llm.generate_data(jsonType, uploadedData, num_records)
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
    global json_data, json_type, visualization_html, saved_json_data, generation_method, generation_time, avg_time_per_record

    # Get JSON type, attributes, and generation method from the form
    json_type = request.form['jsonType']
    selected_attributes = request.form.getlist('attribute')
    generation_method = request.form['generationMethod']
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
    data = generate_data(json_type, uploaded_data, selected_attributes, generation_method, num_records)

    # Convert data to JSON format
    json_data = json.dumps(data, indent=4).encode('utf-8').decode('unicode_escape')

    visualization_html = visualize_data(time_metrics, saved_json_data, generation_method, json_type)

    return render_template('results.html', json_data=json_data, json_type=json_type, visualization_html=visualization_html, saved_json_data=saved_json_data, generation_method=generation_method)


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
    global saved_json_data, json_type, generation_method, time_metrics

    saved_json_data = {
        'json_data': request.form['json_data'],
        'json_type': json_type,
        'generation_method': generation_method,
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
    visualization_html = visualize_data(time_metrics, saved_json_data, generation_method, json_type)
    # Return the results template with updated data
    return render_template('results.html', json_data=json_data, json_type=json_type, visualization_html=visualization_html, saved_json_data=saved_json_data, generation_method=generation_method)


if __name__ == '__main__':
    app.run(debug=True)
