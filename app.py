from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import google.generativeai as genai
import os
import requests

app = Flask(__name__)
CORS(app)

# Configure API key
genai.configure(api_key="AIzaSyAIzUy8Sku93YnxhQRGEWm4LXCHLL1u61k")

prompt = """Analyze the following audio and identify the student's most likely emotion
      (Choose from: surprised, confused, happy, bored).
      
      If any of these scenarios occur with student {Answer correct,
          Enjoy lesson,
          Understand concept,
          Work with peers,
          Feel supported,
          Control learning,
          Celebrate success,
          Connect with friends,
          Learn at own pace,
          Tech works well,
          Prefer online learning} the student is happy.
      
      If any of these scenarios happen {Unexpected announcement
          Guest speaker joins
          Technical glitch occurs
          Teacher makes a joke
          Learn something new
          See classmate online
          Win a game or contest
          Break from routine
          Teacher gives praise
          Unexpected question} the student is surprised.
  
      If any of these scenarios occur {Miss key instruction
          Technical issues arise
          Unclear explanation
          Fast lecture pace
          New vocabulary used
          Complex concept introduced
          Forget key information
          Hear unclear audio
          Lack practice opportunity
          Miss classmate explanation} the student is confused.
      
      If any of these scenarios occur {Repetitive material
          Unengaging activity
          Passive learning style
          Lack of interaction
          Technical difficulties
          Distracting environment
          Unclear learning goals
          Predictable routine
          Slow lecture pace
          Irrelevant content} the student is bored.
      
         Give the Answer in one word which is the most likely emotion & keep it in lowercase."""





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
    



@app.route('/api/v2/audio/audio_to_emotion', methods=['POST'])
def analyze_audio():
    try:
        print("Received request to analyze audio...")
        print("Request data:", request.json)
        # Get the audio_url from the request JSON
        data = request.get_json()
        
        meet_id = data.get('meet_id')
        host_id = data.get('host_id')
        studentPID = data.get('studentPID')
        audio_url = data.get('audio_url')
        time_stamp = data.get('time_stamp')
        
        if not meet_id or not host_id or not studentPID or not audio_url or not time_stamp:
            return jsonify({"error": "Missing required fields: 'meet_id', 'host_id', 'studentPID', 'audio_url', or 'time_stamp"}), 400
        
        # Download the audio file
        audio_path = download_audio_file(audio_url)

        # Upload file to Gemini
        uploaded_file = genai.upload_file(audio_path)

        # Use appropriate model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")  # or gemini-1.5-flash

        # Send file + prompt
        response = model.generate_content([
            prompt,
            uploaded_file
        ])

        if os.path.exists(audio_path):
                os.remove(audio_path)

        emotion = response.text.strip().lower()

        # Prepare the payload for the POST request
        payload = {
            "meet_id": meet_id,
            "host_id": host_id,
            "studentPID": studentPID,
            "audio_url": audio_url,
            "time_stamp": time_stamp,
            "predicted_emotion": emotion
        }

        # Make a POST request to the external endpoint
        external_endpoint = 'https://mood-lens-server.onrender.com/api/v1/audio/audio_to_emotion'
        try:
            external_response = requests.post(external_endpoint, json=payload)
            external_response.raise_for_status()  # Raise an error for non-2xx responses
            # Return the response from the external endpoint
            return jsonify(external_response.json()), external_response.status_code
        except requests.exceptions.RequestException as e:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return jsonify({"error": "Failed to send data to external endpoint", "details": str(e)}), 500
        
    except Exception as e:
        if os.path.exists(audio_path):
                os.remove(audio_path)
        return jsonify({"error": str(e)}), 500


# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))  # use Render's provided port
    app.run(host="0.0.0.0", port=port)
