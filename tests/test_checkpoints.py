from dataclasses import asdict

from phraseframe.services.checkpoints import CheckpointService


def test_checkpoint_service_generates_template_questions() -> None:
    service = CheckpointService()
    questions = service._questions_for_snippet("Attention is a limited resource.")
    assert len(questions) == 3
    assert questions[0].type == "literal"
    payload = [asdict(question) for question in questions]
    assert payload[0]["text"]
