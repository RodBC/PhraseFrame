"""Unit tests for checkpoint scoring."""

from phraseframe.services.checkpoints import CheckpointAnswer, CheckpointQuestion, CheckpointService


def test_score_answers_marks_weak_empty_responses() -> None:
    service = CheckpointService()
    questions = (
        CheckpointQuestion(id="literal", text="What happened?", type="literal"),
        CheckpointQuestion(id="inferential", text="What does it imply?", type="inferential"),
        CheckpointQuestion(id="connection", text="How does it connect?", type="connection"),
    )
    score, weak, feedback, wpm_adjust = service._score_answers(
        questions,
        [
            CheckpointAnswer(text="", confidence="no_idea"),
            CheckpointAnswer(text="Maybe something", confidence="unsure"),
            CheckpointAnswer(text="It connects to earlier ideas", confidence="sure"),
        ],
    )
    assert score < 0.67
    assert weak is True
    assert wpm_adjust == -30
    assert feedback


def test_score_answers_accepts_strong_recall() -> None:
    service = CheckpointService()
    questions = (
        CheckpointQuestion(id="literal", text="What happened?", type="literal"),
        CheckpointQuestion(id="inferential", text="What does it imply?", type="inferential"),
        CheckpointQuestion(id="connection", text="How does it connect?", type="connection"),
    )
    score, weak, _feedback, wpm_adjust = service._score_answers(
        questions,
        [
            CheckpointAnswer(text="A clear specific point about attention.", confidence="sure"),
            CheckpointAnswer(text="It implies sustained focus matters.", confidence="sure"),
            CheckpointAnswer(text="It builds on the opening paragraph.", confidence="sure"),
        ],
    )
    assert score >= 0.9
    assert weak is False
    assert wpm_adjust == 0


def test_extractive_summary_uses_first_three_sentences_and_caps_length() -> None:
    service = CheckpointService()
    summary = service._extractive_summary(
        "Attention is limited. Readers need pauses! Meaning survives when pace is honest? "
        "This fourth sentence must not appear."
    )
    assert summary == (
        "Attention is limited. Readers need pauses! Meaning survives when pace is honest?"
    )
    assert len(service._extractive_summary(("word " * 100) + ".")) <= 400


def test_gaps_from_answers_lists_empty_and_no_idea() -> None:
    service = CheckpointService()
    questions = (
        CheckpointQuestion(id="literal", text="What happened?", type="literal"),
        CheckpointQuestion(id="inferential", text="What does it imply?", type="inferential"),
    )
    gaps = service._gaps_from_answers(
        questions,
        [
            CheckpointAnswer(text="", confidence="no_idea"),
            CheckpointAnswer(text="Maybe", confidence="unsure"),
        ],
    )
    assert len(gaps) == 2
    assert gaps[0].reason == "empty_answer"
    assert gaps[0].question_text == "What happened?"
    assert gaps[1].reason == "unsure"


def test_literal_answers_have_more_weight_in_score() -> None:
    service = CheckpointService()
    questions = (
        CheckpointQuestion(id="literal", text="Main point?", type="literal"),
        CheckpointQuestion(id="connection", text="Connection?", type="connection"),
    )
    literal_missing = service._score_answers(
        questions,
        [
            CheckpointAnswer(text="", confidence="no_idea"),
            CheckpointAnswer(text="A sound connection", confidence="sure"),
        ],
    )[0]
    connection_missing = service._score_answers(
        questions,
        [
            CheckpointAnswer(text="A concrete main point", confidence="sure"),
            CheckpointAnswer(text="", confidence="no_idea"),
        ],
    )[0]
    assert literal_missing < connection_missing


def test_template_question_count_varies_from_two_to_five() -> None:
    service = CheckpointService()
    assert len(service._template_questions("one two three")) == 2
    assert len(service._template_questions(" ".join(["word"] * 20))) == 3
    assert len(service._template_questions(" ".join(["word"] * 120))) == 4
    questions = service._template_questions(" ".join(["word"] * 240))
    assert len(questions) == 5
    assert {question.id for question in questions} >= {"key_detail", "application"}
