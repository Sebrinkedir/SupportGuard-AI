# 🛡️ SupportGuard-AI

SupportGuard-AI is a multi-agent AI system for reliable customer support response generation. Instead of using a single AI, it uses four specialized agents that each review a customer query from a different angle. A formal scoring system then decides what makes it into the final response — ensuring accuracy, policy compliance, and consistency.

---

## The Problem

Most AI support bots use a single model which leads to hallucinated information, policy violations, inconsistent answers, and no way to measure reliability. SupportGuard-AI solves this with a formal, measurable, multi-agent approach.

---

## How It Works

A customer types a query. Four agents analyze it, each returning a response fragment with a confidence score and severity rating. A scoring formula (RAS) filters out low-quality fragments. Only verified fragments make it into the final response. A reliability score is then calculated for the whole system.

---

## The 4 Agents

| Agent | Job | Weight |
|---|---|---|
| Intent Analysis | Classifies query topic and intent | 0.30 |
| Policy Compliance | Ensures response follows company rules | 0.35 |
| Factual Grounding | Verifies claims against FAQ documents | 0.25 |
| Tone & Clarity | Ensures polite and clear language | 0.10 |

---

## RAS Formula
RAS(i) = (wa × Si × Ca,i) / total_weight

- wa = agent weight
- Si = severity score (high=1.0, medium=0.6, low=0.2)
- Ca,i = agent confidence (0 to 1)

Fragments with RAS below 0.08 are rejected.

---

## Reliability Model
R = α(1 − HR) + βPCS + γStability

- HR = Hallucination Rate
- PCS = Policy Compliance Score
- Stability = 1 − standard deviation of RAS across runs
- α=0.4, β=0.4, γ=0.2

---

## Project Structure
SupportGuard-AI/
├── agents/          → The 4 AI agents
├── tools/           → MCP policy and FAQ lookup tools
├── data/            → Support documents
├── evaluation/      → Evaluation scripts
├── templates/       → Web UI
├── arbitration.py   → RAS scoring
├── reliability.py   → Reliability model
├── main.py          → Main pipeline
├── app.py           → Flask web interface
└── config.py        → Settings and weights

---

## Built With

- Python 3.13
- Google Gemini API (gemini-2.5-flash)
- Flask
- google-genai
- python-dotenv

---

## Author

Sebrina — BSc Computer Science
Peter — BSc Computer Science
Sujit — BSc Computer Science
Hamza — BSc Computer Science