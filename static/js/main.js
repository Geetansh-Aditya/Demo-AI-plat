require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});

require(['vs/editor/editor.main'], function() {
    window.editor = monaco.editor.create(document.getElementById('monaco-editor'), {
        value: '# Start By Writing Your Code Below',
        language: 'python',
        theme: 'vs-light',
        minimap: { enabled: false },
        fontSize: 14,
        automaticLayout: true,
        scrollBeyondLastLine: false,
        lineNumbers: 'on',
        readOnly: false
    });

    monaco.editor.defineTheme('leetcode-light', {
        base: 'vs',
        inherit: true,
        rules: [],
        colors: {
            'editor.background': '#ffffff',
        }
    });

    monaco.editor.setTheme('leetcode-light');
});

function appendToTerminal(text, type = 'normal') {
    const terminal = document.getElementById('terminal-content');
    const line = document.createElement('div');
    line.className = `output-line ${type}`;
    line.textContent = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

async function runCode() {
    const editorContent = window.editor.getValue();
    const selectedLanguage = document.querySelector('.language-select').value;

    appendToTerminal('Running code...', 'normal');

    try {
        const response = await fetch('/execute-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: editorContent, language: selectedLanguage }),
        });

        if (!response.ok) throw new Error('Failed to execute code');

        const result = await response.json();
        if (result.stdout) appendToTerminal(result.stdout, 'success');
        if (result.stderr) appendToTerminal(result.stderr, 'error');
    } catch (error) {
        appendToTerminal(`Error: ${error.message}`, 'error');
    }
}


function submitCode() {
    const code = window.editor.getValue(); // Retrieve code from the Monaco editor
    const testCasesInput = document.getElementById('testCases').value;

    let testcases;
    try {
        testcases = JSON.parse(testCasesInput); // Ensure test cases are in valid JSON format
    } catch (error) {
        appendToTerminal('Error: Invalid test cases format', 'error');
        return;
    }

    // Create the JSON object for submission
    const submissionData = {
        code: code,
        testcases: testcases
    };

    appendToTerminal('Submitting solution...', 'normal');

    // Send POST request to the /submit-code endpoint
    fetch('/submit-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(submissionData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        appendToTerminal('Solution submitted successfully!', 'success');
        appendToTerminal('Response: ' + JSON.stringify(data), 'normal');
    })
    .catch(error => {
        appendToTerminal('Error: ' + error.message, 'error');
    });
}



document.querySelector('.language-select').addEventListener('change', function(e) {
    const language = e.target.value;
    const starterCode = {
        javascript: `/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
var twoSum = function(nums, target) {
    // Your code here
};`,
        python: `class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your code here
        pass`,
        java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Your code here
        return null;
    }
}`,
        cpp: `class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Your code here
        return {};
    }
};`
    };

    monaco.editor.getModels()[0].setValue(starterCode[language]);
    monaco.editor.setModelLanguage(monaco.editor.getModels()[0], language);
});

//

async function fetchProblem() {
    const apiUrl = '/get-problems';
    try {
        const response = await fetch(apiUrl, { method: 'POST' });
        if (!response.ok) {
            throw new Error('Failed to fetch problem');
        }
        const data = await response.json();

        // Extract and display problem details
        document.getElementById('problem-title').innerText = data.topic;
        document.getElementById('problem-description').innerHTML = `<strong><pre>${data.content || 'No content available'}</pre></strong>`;
        const exampleSection = document.getElementById('example-section');
        exampleSection.innerHTML = ''; // Clear previous examples

        // Populate examples in UI
        data.test_cases.forEach((testCase, index) => {
            const para = document.createElement('p');
            para.textContent = `Test Case ${index + 1}: Input: ${JSON.stringify(testCase.input)}, Output: ${testCase.expected_output}`;
            exampleSection.appendChild(para);
        });

        // Populate test cases in a dedicated input field
        const testCasesField = document.getElementById('testCases');
        testCasesField.value = JSON.stringify(data.test_cases, null, 2); // For easier editing
    } catch (error) {
        console.error('Error fetching problem:', error);
        document.getElementById('problem-title').innerText = 'Error loading problem';
        document.getElementById('problem-description').innerHTML = `<p>${error.message}</p>`;
    }
}



window.onload = fetchProblem;

