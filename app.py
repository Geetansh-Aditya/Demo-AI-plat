from flask import Flask, render_template, request, jsonify
import requests
import json
import subprocess
import tempfile
import os
import temporary

app = Flask(__name__)
LLM_Endpoint = "http://127.0.0.1:8000"

@app.route('/')
def index():
    return render_template('index.html')


# Endpoint to get the problems fetched to the website
@app.route('/get-problems', methods=['POST'])
def get_problems():
    try:
        # topic = requests.post(f"{LLM_Endpoint}/gues_gen").json()['topic']['content']
        # json_payload = {'topic': topic, "difficulty": "medium"}
        # response = requests.post(url=f"{LLM_Endpoint}/generate_questions", json=json_payload)
        # if response.status_code == 200:
        #     contents = response.json()['questions']['content']
        #     contents = json.loads(contents)
        #     test_cases = generate_test_cases(contents['question'])



            # return jsonify({"content": contents['question'], "topic": contents['title'], "test_cases": test_cases['content']})
        with open('hard.json', 'r') as f:
            data = json.load(f)
        return data
        # else:
        #     return jsonify({"error": "Failed to fetch questions from API"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Code Execution
@app.route('/execute-code', methods=['POST'])
def execute_code():
    response = requests.post(url='http://127.0.0.1:5001/run-python', json=request.json)
    return response.json()


# Generating Test Cases
def generate_test_cases(question):
    test_case_ques = {"question" : question}
    response = requests.post(f"{LLM_Endpoint}/generate_test_cases", json=test_case_ques)
    return response.json()['test_cases']


# Mechanism to Submit the code
@app.route('/submit-code', methods=['POST'])
def submit_code():
    # Parse incoming JSON data
    data = request.json
    code = data['code']
    test_cases = data['testcases']

    # Save the code to a temporary file
    temp_file = 'temporary.py'
    with open(temp_file, 'w') as f:
        f.write(code)

    results = []

    # Iterate over the test cases
    for test_case in test_cases:
        inputs, expected_output = test_case['input'], test_case['expected_output']
        result = temporary.sum_of_two_numbers(*inputs.values())
        results.append(result==expected_output)


    # Return the results as a JSON response
    return jsonify({"results": results})



# Calling the Flask Application
if __name__ == '__main__':
    app.run(debug=True)