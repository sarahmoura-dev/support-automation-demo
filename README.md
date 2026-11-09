# Support Automation Demo

A small, self-contained demo of a **customer-message automation backend**: it receives messages through a webhook, classifies the intent, stores everything, and returns a suggested reply, flagging urgent or unclear messages for a human.

It mirrors the pattern I use in production WhatsApp / n8n automations, rebuilt here with **fictional data only** (no client code or data).

## Features

- `POST /webhook`: receives `{from, text}`, returns intent, urgency, confidence, suggested reply and an `escalate_to_human` flag
- Rule-based intent classifier (pricing, scheduling, support, cancellation), accent-insensitive, works in English and Portuguese
- Pluggable `classifier` interface, so an LLM-based classifier can replace the rules without touching the API
- SQLite storage, `GET /messages` and `GET /stats`
- Automated tests with pytest

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

Try it:

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+5500000000000", "text": "How much does a quote cost? It is urgent"}'
```

```json
{"id": 1, "intent": "pricing", "urgent": true, "confidence": 1.0,
 "reply": "Thanks for your interest! A team member will send you a quote shortly.",
 "escalate_to_human": true}
```

## Tests

```bash
pytest -q
```

## Using it with n8n

Point an n8n **HTTP Request** node at `/webhook` after your WhatsApp/Telegram trigger node, then branch on `escalate_to_human` to either send the suggested reply or notify a person.

## Stack

Python · Flask · SQLite · pytest

## Author

Sarah Moura, Software Developer & AI Automation Specialist
[LinkedIn](https://www.linkedin.com/in/sarahmoura-dev) · [Portfolio](https://sarah-moura-portfolio.netlify.app)
