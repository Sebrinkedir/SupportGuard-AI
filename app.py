from flask import Flask, render_template, request, jsonify
from main import run_supportguard

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    result = run_supportguard(query)
    return jsonify({
        "response": result["final_response"],
        "ras": result["arbitration"]["average_ras"],
        "reliability": result["reliability"]["reliability_score"],
        "approved": len(result["arbitration"]["approved_fragments"]),
        "rejected": len(result["arbitration"]["rejected_fragments"])
    })

if __name__ == "__main__":
    app.run(debug=True)