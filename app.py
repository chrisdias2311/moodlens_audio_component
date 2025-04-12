from flask import Flask, jsonify, request
import google.generativeai as genai
import os
import requests

app = Flask(__name__)

# Configure API key
genai.configure(api_key="AIzaSyBrIph-OSVnPnbeq11CvRpQEv4irTY6yCU")

def download_audio_file(audio_url, output_path="audio.mp3"):
    """
    Downloads an audio file from the given URL and saves it to the specified path.
    """
    try:
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        with open(output_path, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to download audio file: {str(e)}")

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    try:
        # Get the audio_url from the request JSON
        data = request.get_json()
        if not data or 'audio_url' not in data:
            return jsonify({"error": "Missing 'audio_url' in request body"}), 400

        audio_url = data['audio_url']

        # Download the audio file
        audio_path = download_audio_file(audio_url)

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

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use Render's provided port
    app.run(host="0.0.0.0", port=port)
