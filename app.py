from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re

app = Flask(__name__)
CORS(app)

def extractResponse(input_output_string):
    pairs = input_output_string.strip().split('\n')
    cleaned_text = []

    for i in range(0, len(pairs)-1, 2):
        input_line = pairs[i].strip()[4:]  # Skip "[I]: " prefix
        output_line = pairs[i+1].strip()[4:]  # Skip "[O]: " prefix

        # Remove unnecessary punctuations
        cleaned_input = re.sub(r'[^\w\s]', '', input_line)
        cleaned_output = re.sub(r'[^\w\s]', '', output_line)

        # Skip sequences starting with "[I]"
        if not cleaned_input.startswith("[I]"):
            cleaned_text.append(cleaned_output)

    # Concatenate the cleaned output lines
    concatenated_output = ' '.join(cleaned_text)
    return concatenated_output

@app.route('/generate-text', methods=['POST'])
def generate_text():
    input_text = request.json.get('text')
    response = requests.post(
        "https://api-inference.huggingface.co/models/MwangiNelson/RevisedNutribot",
        headers={"Authorization": "Bearer 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"},
        json={"inputs": input_text, "parameters": {"max_length": 45, "temperature": 0.75}}
    )

    if response.status_code == 200:
        generated_text = response.json()[0]['generated_text']
        filtered_text = extractResponse(generated_text)
        
        # Additional metadata
        metadata = {
            "status": "success",
            "message": "Text generated successfully",
            "input_length": len(input_text),
            "output_length": len(generated_text),
            # Add more metadata as needed
        }

        return jsonify({"metadata": metadata, "filtered_text": filtered_text, "raw_text": generated_text})
    else:
        # Error metadata
        error_metadata = {
            "status": "error",
            "message": f"Error from Hugging Face API: {response.text}",
            "input_length": len(input_text),
        }

        return jsonify({"metadata": error_metadata}), response.status_code

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
