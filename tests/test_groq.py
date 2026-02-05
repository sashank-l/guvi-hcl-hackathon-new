import types

import app.agent as agent


def test_groq_used_for_reply(monkeypatch):
    class _FakeChoice:
        def __init__(self, text):
            self.message = types.SimpleNamespace(content=text)

    class _FakeResponse:
        def __init__(self, text):
            self.choices = [_FakeChoice(text)]

    class _FakeChat:
        def __init__(self):
            self.completions = self

        def create(self, **kwargs):
            return _FakeResponse("Please share your branch name, sirji?")

    class _FakeGroq:
        def __init__(self, api_key, base_url):
            self.chat = _FakeChat()

    monkeypatch.setattr(agent, "GROQ_API_KEY", "test-key")
    monkeypatch.setattr(agent, "Groq", _FakeGroq)

    reply = agent.build_reply(
        history=[],
        current_text="Your account will be blocked, send OTP",
        identity={"name": "Ramesh", "age": 45, "city": "Pune", "role": "citizen"},
        language="English",
        scam_type="general",
    )

    assert "branch" in reply["reply"].lower()


def test_groq_failure_falls_back(monkeypatch):
    class _FakeGroq:
        def __init__(self, api_key, base_url):
            raise RuntimeError("boom")

    monkeypatch.setattr(agent, "GROQ_API_KEY", "test-key")
    monkeypatch.setattr(agent, "Groq", _FakeGroq)

    reply = agent.build_reply(
        history=[],
        current_text="Send OTP now",
        identity={"name": "Ravi", "age": 40, "city": "Delhi", "role": "citizen"},
        language="English",
        scam_type="general",
    )

    assert "otp" in reply["reply"].lower()
