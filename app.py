from flask import Flask, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure API key
genai.configure(api_key="AIzaSyBrIph-OSVnPnbeq11CvRpQEv4irTY6yCU")

@app.route('/analyze-audio', methods=['GET'])
def analyze_audio():
    try:
        audio_path = "lecture_1.mp3"  # Update path as needed

        # Upload file to Gemini
        uploaded_file = genai.upload_file(audio_path)

        # Use appropriate model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")  # or gemini-1.5-flash

        # Send file + prompt
        response = model.generate_content([
            "Describe this audio clip",
            uploaded_file
        ])

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
