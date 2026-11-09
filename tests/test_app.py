import pytest
from app.main import create_app
from app.classifier import RuleClassifier


@pytest.fixture
def client(tmp_path):
    return create_app(str(tmp_path / "t.db")).test_client()


@pytest.mark.parametrize("text,intent", [
    ("How much does it cost?", "pricing"),
    ("I want to schedule an appointment", "schedule"),
    ("The app is not working, error on login", "support"),
    ("Please cancel my plan", "cancel"),
    ("hello there", "other"),
    ("Qual o valor do orçamento?", "pricing"),
])
def test_intents(text, intent):
    assert RuleClassifier().classify(text).intent == intent


def test_urgent_escalates(client):
    r = client.post("/webhook", json={"from": "+550000000000", "text": "URGENT, help me now"}).get_json()
    assert r["urgent"] and r["escalate_to_human"]


def test_validation(client):
    assert client.post("/webhook", json={"text": "hi"}).status_code == 400


def test_stats(client):
    client.post("/webhook", json={"from": "a", "text": "price?"})
    client.post("/webhook", json={"from": "b", "text": "quote please"})
    assert client.get("/stats").get_json() == {"pricing": 2}
