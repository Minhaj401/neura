
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os

# 🔐 Optional but helpful: Force Gemini to NOT use Vertex AI credentials
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"

# ⚠️ Hardcoded API key (use only for testing, never for production)
client = genai.Client(api_key="")


app = Flask(__name__)
CORS(app)

PROMPT = (
    "What is the emotional tone expressed in this image? "
    "Reply with only one word: positive, negative, or neutral."
)

@app.route('/analyze_image_sentiment', methods=['POST'])
def analyze():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image provided'}), 400

    img_bytes = file.read()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "parts": [
                        {"inline_data": {"mime_type": file.mimetype, "data": img_bytes}},
                        {"text": PROMPT}
                    ]
                }
            ]
        )
        print("Gemini API response:", response)
        sentiment = response.text.strip().lower()
        if sentiment not in ['positive', 'negative', 'neutral']:
            sentiment = 'neutral'
        return jsonify({'sentiment': sentiment})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
