from flask import Flask, render_template, request, jsonify
from main import run_supportguard

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "").strip()
    history = data.get("history", [])
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Check for simple conversational messages
    simple_responses = [
        "thank you", "thanks", "okay", "ok", "bye", "goodbye",
        "great", "perfect", "got it", "understood", "alright",
        "okay thank you", "ok thanks", "thank you so much", "cheers"
    ]
    if query.lower() in simple_responses or len(query.split()) <= 3 and any(word in query.lower() for word in ["thank", "ok", "bye", "great", "perfect"]):
        return jsonify({
            "response": "You're welcome! 😊 Feel free to reach out if you have any other questions. Have a great day!",
            "ras": "N/A",
            "reliability": "N/A",
            "approved": "N/A",
            "rejected": "N/A"
        })

    # Build context from history for follow-up awareness
    if len(history) > 1:
        context = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history[:-1]])
        full_query = f"Previous conversation:\n{context}\n\nCurrent question: {query}"
    else:
        full_query = query

    result = run_supportguard(full_query)
    return jsonify({
        "response": result["final_response"],
        "ras": result["arbitration"]["average_ras"],
        "reliability": result["reliability"]["reliability_score"],
        "approved": len(result["arbitration"]["approved_fragments"]),
        "rejected": len(result["arbitration"]["rejected_fragments"])
    })
if __name__ == "__main__":
    app.run(debug=True)