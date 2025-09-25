from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["GET"])
def me():
    return "Hello! I'm a dummy chatbot server"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    return jsonify({
        "user_message": message,
        "bot_reply": "Hello! I'm a dummy chatbot "
    })


if __name__ == "__main__":
    app.run(port=9000, debug=True)
