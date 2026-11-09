import os
from flask import Flask, jsonify, request
from .classifier import RuleClassifier
from .storage import Storage

REPLIES = {
    "pricing": "Thanks for your interest! A team member will send you a quote shortly.",
    "schedule": "Happy to help you book a time. What day works best for you?",
    "support": "Sorry about that! We've opened a support ticket and will reply soon.",
    "cancel": "We're sorry to see you go. A team member will contact you to confirm.",
    "other": "Thanks for your message! A team member will get back to you.",
}


def create_app(db_path: str | None = None, classifier=None) -> Flask:
    app = Flask(__name__)
    store = Storage(db_path or os.getenv("DB_PATH", "demo.db"))
    clf = classifier or RuleClassifier()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/webhook")
    def webhook():
        data = request.get_json(silent=True) or {}
        sender, text = data.get("from"), (data.get("text") or "").strip()
        if not sender or not text:
            return jsonify(error="fields 'from' and 'text' are required"), 400
        result = clf.classify(text)
        msg_id = store.add(sender, text, result)
        return jsonify(id=msg_id, intent=result.intent, urgent=result.urgent,
                       confidence=result.confidence, reply=REPLIES[result.intent],
                       escalate_to_human=result.urgent or result.intent == "other")

    @app.get("/messages")
    def messages():
        return jsonify(store.recent())

    @app.get("/stats")
    def stats():
        return jsonify(store.stats())

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
