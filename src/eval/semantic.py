from sentence_transformers import SentenceTransformer, util
import sys

class SemanticEvaluator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"DEBUG: Initializing SemanticEvaluator with {model_name}")
        try:
            # Load model lazily or immediately
            self.model = SentenceTransformer(model_name)
            self.disabled = False
        except Exception as e:
            print(f"WARNING: Failed to load SentenceTransformer: {e}")
            print("Semantic evaluation will be disabled (return 0.0)")
            self.disabled = True

    def compute_similarity(self, text1: str, text2: str) -> float:
        if self.disabled or not text1 or not text2:
            return 0.0
            
        try:
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            score = util.cos_sim(embeddings[0], embeddings[1])
            return float(score.item())
        except Exception as e:
            print(f"ERROR: Semantic computation failed: {e}")
            return 0.0
