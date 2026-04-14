import os
import importlib
import pytest

# Provide a dummy key so the OpenAI client can be instantiated without a real credential.
os.environ.setdefault("OPENAI_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def _restore_prompt_version():
    original = os.environ.get("PROMPT_VERSION")
    yield
    if original is None:
        os.environ.pop("PROMPT_VERSION", None)
    else:
        os.environ["PROMPT_VERSION"] = original


def test_default_prompt_version_is_v1():
    os.environ.pop("PROMPT_VERSION", None)
    import clinicflow.backend.services.agents_service as svc
    importlib.reload(svc)
    assert svc.ACTIVE_PROMPT_VERSION == "v1"


def test_prompt_version_v2_loads_from_env():
    os.environ["PROMPT_VERSION"] = "v2"
    import clinicflow.backend.services.agents_service as svc
    importlib.reload(svc)
    assert svc.ACTIVE_PROMPT_VERSION == "v2"
    assert "conservative" in svc.PROMPTS["v2"]


def test_all_prompts_have_required_json_instruction():
    import clinicflow.backend.services.agents_service as svc
    importlib.reload(svc)
    for version, text in svc.PROMPTS.items():
        assert "JSON" in text, f"Prompt {version} must instruct JSON output"
