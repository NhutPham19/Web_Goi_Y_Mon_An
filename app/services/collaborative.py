"""
app/services/collaborative.py
Collaborative Filtering — SVD Matrix Factorization (scikit-surprise).
Kích hoạt khi DB có >= 200 ratings (Task 4.4).

Skeleton được tạo ở Phase 1 để import không lỗi.
Implementation đầy đủ ở Task 4.4.
"""
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "cf_model.pkl")


def train_cf_model():
    """
    Train SVD model trên toàn bộ ratings hiện có.
    Serialize model ra disk với joblib.
    Gọi thủ công hoặc từ script seed.
    """
    try:
        from surprise import SVD, Dataset, Reader
        from surprise.model_selection import train_test_split
        import pandas as pd
        from app.models.rating import Rating
        from app import db

        rows = db.session.query(
            Rating.user_id, Rating.recipe_id, Rating.score
        ).all()

        if len(rows) < 200:
            print(f"[CF] Chỉ có {len(rows)} ratings — cần ít nhất 200 để train CF.")
            return None

        df = pd.DataFrame(rows, columns=["user_id", "recipe_id", "score"])
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(df[["user_id", "recipe_id", "score"]], reader)
        trainset = dataset.build_full_trainset()

        model = SVD(n_factors=50, n_epochs=20, random_state=42)
        model.fit(trainset)

        joblib.dump(model, MODEL_PATH)
        print(f"[CF] Model trained và lưu tại {MODEL_PATH}")
        return model

    except ImportError:
        print("[CF] scikit-surprise chưa được cài — bỏ qua CF training.")
        return None


def compute_cf_recommendations(user_id: str, top_n: int = 10) -> list:
    """
    Dự đoán rating cho tất cả recipes user chưa rate.
    Returns: List[(recipe_id, predicted_score)]
    """
    if not os.path.exists(MODEL_PATH):
        return []

    try:
        model = joblib.load(MODEL_PATH)
        from app.models.recipe import Recipe
        from app.models.rating import Rating

        # Recipes user đã rate
        rated_ids = {
            r.recipe_id
            for r in Rating.query.filter_by(user_id=user_id).all()
        }

        # Tất cả published recipes
        all_recipes = Recipe.query.filter_by(is_published=True).all()
        unrated = [r for r in all_recipes if r.id not in rated_ids]

        predictions = []
        for recipe in unrated:
            pred = model.predict(str(user_id), str(recipe.id))
            predictions.append((recipe.id, pred.est))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:top_n]

    except Exception as e:
        print(f"[CF] Lỗi khi predict: {e}")
        return []
