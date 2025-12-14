from sentence_transformers import SentenceTransformer, util

class SemanticEvaluator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load model lazily or immediately
        self.model = SentenceTransformer(model_name)

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
            
        embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
        score = util.cos_sim(embeddings[0], embeddings[1])
        return float(score.item())
