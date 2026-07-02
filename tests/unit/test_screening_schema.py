import pytest

from app.schemas.screening import ScreeningResult


class TestScreeningResult:
    def test_valid_screening_result(self):
        result = ScreeningResult(
            candidate_summary="Experienced Python developer",
            fit_score=0.85,
            strengths=["Python", "FastAPI", "Docker"],
            risks=["No cloud experience"],
            follow_up_questions=["Can you describe a production issue?"],
            confidence=0.9,
        )
        assert result.fit_score == 0.85
        assert result.confidence == 0.9
        assert len(result.strengths) == 3
        assert len(result.risks) == 1

    def test_score_rounding(self):
        result = ScreeningResult(
            candidate_summary="Test",
            fit_score=0.853,
            strengths=[],
            risks=[],
            follow_up_questions=[],
            confidence=0.901,
        )
        assert result.fit_score == 0.85
        assert result.confidence == 0.9

    def test_score_validation(self):
        with pytest.raises(Exception):
            ScreeningResult(
                candidate_summary="Test",
                fit_score=1.5,
                strengths=[],
                risks=[],
                follow_up_questions=[],
                confidence=0.5,
            )
