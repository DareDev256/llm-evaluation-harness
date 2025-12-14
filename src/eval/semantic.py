class SemanticEvaluator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Delay importing large deps until we actually need them to avoid slow start/hangs in CI.
        self.model_name = model_name
        self.model = None
        self.util = None
        self.disabled = False

    def _ensure_model(self):
        if self.disabled or self.model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer, util
            self.model = SentenceTransformer(self.model_name)
            self.util = util
        except Exception as e:
            print(f"WARNING: Failed to load SentenceTransformer: {e}")
            print("Semantic evaluation will be disabled (return 0.0)")
            self.disabled = True

    def compute_similarity(self, text1: str, text2: str) -> float:
        if self.disabled or not text1 or not text2:
            return 0.0

        self._ensure_model()
        if self.disabled or self.model is None or self.util is None:
            return 0.0

        try:
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            score = self.util.cos_sim(embeddings[0], embeddings[1])
            return float(score.item())
        except Exception as e:
            print(f"ERROR: Semantic computation failed: {e}")
            self.disabled = True
            return 0.0
