from flask import Flask, request, jsonify, render_template, send_from_directory
from data_generator import generate_synthetic_data
from flask_bootstrap import Bootstrap

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/badges')
def badges():
    return render_template('badges.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Assuming the file is always JSON for simplicity
    json_data = file.read().decode('utf-8')

    # Generate synthetic data
    synthetic_data = generate_synthetic_data(json_data)

    return jsonify({'synthetic_data': synthetic_data})


if __name__ == '__main__':
    app.run(debug=True)
