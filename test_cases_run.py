import json
import inspect


def sum_of_two_numbers(a, b):
    return a + b


with open('hard.json') as file:
    content = json.load(file)

a = len(inspect.signature(sum_of_two_numbers).parameters)
test_cases = content['test_cases']

for test_case in test_cases:
    inputs, outputs = test_case['input'], test_case['expected_output']

    if a == len(inputs):
        result = sum_of_two_numbers(*inputs.values())  # Unpack the values as arguments
        print(result==outputs)
