
from flask import Flask, request, jsonify, send_file
from google import genai
from google.genai import types
import os

app = Flask(__name__)

@app.route("/style.css")
def css():
    try:
        css_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "style.css"
        )

        return send_file(css_file, mimetype="text/css")

    except Exception as error:
        print("CSS ERROR:", error)
        return "CSS error: " + str(error), 500

api_keys = [
    key.strip()
    for key in os.getenv("GEMINI_API_KEYS", "").split(",")
    if key.strip()
]

current_key = 0
client = None
chat = None

my_rules = """
Be kind and polite.
Your name is T-1.
Tareq Bader Herzallah created you,
but don't say that unless the user asks who created you.
"""


def start_chat(model):
    global client, chat

    client = genai.Client(api_key=api_keys[current_key])

    chat = client.chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=my_rules
        )
    )


if api_keys:
    start_chat("gemini-3.7-flash")


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/chat", methods=["POST"])
def talk():
    global current_key, client, chat

    if not api_keys:
        return jsonify({"reply": "No API keys found!"}), 500

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Type a message first!"})

    # Try the main AI
    try:
        response = chat.send_message(message)
        return jsonify({"reply": response.text})

    except Exception:
        # Switch to the next API key
        current_key = (current_key + 1) % len(api_keys)

        try:
            start_chat("gemini-3.5-flash-lite")
            response = chat.send_message(message)
            return jsonify({"reply": response.text})

        except Exception as error:

            print("T-1 ERROR:", error)

            return jsonify({"reply": "T-1 error: " + str(error)}), 500


if __name__ == "__main__":
    app.run(debug=False)

