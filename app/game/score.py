class ScoreState:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hit_count = 0
        self.miss_count = 0
        self.perfect_count = 0
        self.good_count = 0

    def apply_result(self, result: str | None):
        if result == "PERFECT":
            self.score += 1000
            self.combo += 1
            self.hit_count += 1
            self.perfect_count += 1
        elif result == "GOOD":
            self.score += 500
            self.combo += 1
            self.hit_count += 1
            self.good_count += 1
        elif result == "MISS":
            self.combo = 0
            self.miss_count += 1
        self.max_combo = max(self.max_combo, self.combo)

    @property
    def judged_count(self) -> int:
        return self.hit_count + self.miss_count

    @property
    def accuracy(self) -> float:
        total = self.judged_count
        if total <= 0:
            return 0.0
        earned = self.perfect_count * 1000 + self.good_count * 500
        return earned / (total * 1000) * 100.0

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "combo": self.combo,
            "max_combo": self.max_combo,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "perfect_count": self.perfect_count,
            "good_count": self.good_count,
            "accuracy": self.accuracy,
        }

