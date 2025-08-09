from typing import Tuple

class ResumeScorer:
    def __init__(self, suitable_threshold: float = 0.8, maybe_threshold: float = 0.5):
        """
        Args:
            suitable_threshold: Score above which a resume is considered 'Suitable'
            maybe_threshold: Score above which a resume is considered 'Maybe Suitable'
        """
        self.suitable_threshold = suitable_threshold
        self.maybe_threshold = maybe_threshold

    def classify(self, score: float) -> str:
        """
        Classify a resume based on its score.
        """
        if score >= self.suitable_threshold:
            return "Suitable"
        elif score >= self.maybe_threshold:
            return "Maybe Suitable"
        else:
            return "Not Suitable"

    def score_resume(self, composite_score: float) -> Tuple[str, float]:
        """
        Return both label and score for convenience.
        """
        label = self.classify(composite_score)
        return label, composite_score
