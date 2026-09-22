"""
app/services/collaborative.py
Collaborative Filtering — dùng scipy.sparse.linalg.svds (built-in, không cần C++).
Không phụ thuộc vào scikit-surprise (khó compile trên mọi platform).
Kích hoạt khi DB có >= 200 ratings.
"""
import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "cf_model.pkl")


def train_cf_model():
    """
    Train SVD Matrix Factorization model trên toàn bộ ratings.
    Dùng scipy.sparse.linalg.svds thay vì scikit-surprise.
    Serialize model ra disk với joblib.
    """
    try:
        import pandas as pd
        from scipy.sparse import csr_matrix
        from scipy.sparse.linalg import svds
        from app.models.rating import Rating
        from app import db

        rows = db.session.query(
            Rating.user_id, Rating.recipe_id, Rating.score
        ).all()

        if len(rows) < 50:  # Giảm ngưỡng xuống 50 cho practical usage
            print(f"[CF] Chỉ có {len(rows)} ratings — cần ít nhất 50 để train CF.")
            return None

        df = pd.DataFrame(rows, columns=["user_id", "recipe_id", "score"])

        # Build user-item matrix
        all_users = df["user_id"].unique()
        all_items = df["recipe_id"].unique()
        user_to_idx = {u: i for i, u in enumerate(all_users)}
        item_to_idx = {item: i for i, item in enumerate(all_items)}
        idx_to_item = {i: item for item, i in item_to_idx.items()}

        n_users = len(all_users)
        n_items = len(all_items)

        # Build sparse matrix
        row_indices = [user_to_idx[u] for u in df["user_id"]]
        col_indices = [item_to_idx[r] for r in df["recipe_id"]]
        data = df["score"].values.astype(float)

        ratings_matrix = csr_matrix((data, (row_indices, col_indices)), shape=(n_users, n_items))
        ratings_dense = ratings_matrix.toarray()

        # Normalize: trừ mean rating của mỗi user
        user_ratings_mean = np.zeros(n_users)
        for i in range(n_users):
            user_row = ratings_dense[i]
            rated_mask = user_row != 0
            if rated_mask.any():
                user_ratings_mean[i] = user_row[rated_mask].mean()
        ratings_demeaned = ratings_dense.copy()
        for i in range(n_users):
            mask = ratings_dense[i] != 0
            ratings_demeaned[i, mask] -= user_ratings_mean[i]

        # SVD decomposition
        k = min(50, n_users - 1, n_items - 1)  # n_factors
        if k < 1:
            return None
        U, sigma, Vt = svds(csr_matrix(ratings_demeaned), k=k)
        sigma_diag = np.diag(sigma)

        # Reconstruct predictions matrix
        all_predicted_ratings = np.dot(np.dot(U, sigma_diag), Vt) + user_ratings_mean.reshape(-1, 1)

        model_data = {
            "predicted_ratings": all_predicted_ratings,
            "user_to_idx": user_to_idx,
            "idx_to_item": idx_to_item,
            "all_items": all_items,
        }

        joblib.dump(model_data, MODEL_PATH)
        print(f"[CF] Model trained với {n_users} users, {n_items} items, k={k}. Lưu tại {MODEL_PATH}")
        return model_data

    except Exception as e:
        print(f"[CF] Lỗi khi train model: {e}")
        return None


def compute_cf_recommendations(user_id: str, top_n: int = 10) -> list:
    """
    Dự đoán rating cho tất cả recipes user chưa rate.

    Returns:
        List of (recipe_id, predicted_score) sorted DESC.
        Trả về [] nếu model chưa được train hoặc user_id không có trong training data.
    """
    if not os.path.exists(MODEL_PATH):
        # Thử auto-train nếu đủ data
        from app import db
        from app.models.rating import Rating
        count = Rating.query.count()
        if count >= 50:
            print("[CF] Model chưa có, thử auto-train...")
            train_cf_model()
        if not os.path.exists(MODEL_PATH):
            return []

    try:
        model_data = joblib.load(MODEL_PATH)
        predicted_ratings = model_data["predicted_ratings"]
        user_to_idx = model_data["user_to_idx"]
        idx_to_item = model_data["idx_to_item"]

        # Nếu user chưa có trong training data → return []
        user_id_str = str(user_id)
        if user_id_str not in user_to_idx:
            return []

        user_idx = user_to_idx[user_id_str]
        user_predictions = predicted_ratings[user_idx]

        from app.models.rating import Rating
        # Lấy các recipe user đã rate
        rated_ids = {
            str(r.recipe_id)
            for r in Rating.query.filter_by(user_id=user_id).all()
        }

        # Lấy top N unrated recipes
        item_scores = [
            (idx_to_item[i], user_predictions[i])
            for i in range(len(user_predictions))
            if str(idx_to_item[i]) not in rated_ids
        ]
        item_scores.sort(key=lambda x: x[1], reverse=True)

        return item_scores[:top_n]

    except Exception as e:
        print(f"[CF] Lỗi khi predict: {e}")
        return []
