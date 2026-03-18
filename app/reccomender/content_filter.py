import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.db_helper import connect_to_db, close_connection
import pickle
import os

class ContentFilter:
    """
    Content filter class with cached matrices for performance
    """
    
    # Class-level cache variables (shared across instances)
    _anime_data = None
    _cosine_sim = None
    _indices = None
    _cache_file = "content_filter_cache.pkl"
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._ensure_data_loaded()
        self.high_rated_anime = self.get_user_high_rated_anime(user_id)

    def _ensure_data_loaded(self):
        """Load and cache data if not already loaded"""
        if ContentFilter._anime_data is None:
            if os.path.exists(self._cache_file):
                print("Loading cached content filter data...")
                self._load_from_cache()
            else:
                print("Computing content filter matrices (first time only)...")
                self._compute_and_cache_data()

    def _load_from_cache(self):
        """Load precomputed data from cache file"""
        try:
            with open(self._cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                ContentFilter._anime_data = cache_data['anime_data']
                ContentFilter._cosine_sim = cache_data['cosine_sim']
                ContentFilter._indices = cache_data['indices']
            print("Cache loaded successfully!")
        except Exception as e:
            print(f"Failed to load cache: {e}. Recomputing...")
            self._compute_and_cache_data()

    def _compute_and_cache_data(self):
        """Compute TF-IDF and similarity matrices, then cache them"""
        # Load anime data
        df = self.load_anime_data()
        
        # Create TF-IDF matrix
        tfidf = TfidfVectorizer(min_df=5, max_df=0.8, stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['content_string'])
        
        # Compute cosine similarity
        cosine_sim = cosine_similarity(tfidf_matrix)
        
        # Create index mapping
        indices = pd.Series(df.index, index=df['mal_id'])
        
        # Cache the results
        ContentFilter._anime_data = df
        ContentFilter._cosine_sim = cosine_sim
        ContentFilter._indices = indices
        
        # Save to file
        try:
            cache_data = {
                'anime_data': df,
                'cosine_sim': cosine_sim,
                'indices': indices
            }
            with open(self._cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print("Data computed and cached successfully!")
        except Exception as e:
            print(f"Warning: Failed to cache data: {e}")

    def load_anime_data(self):
        """Load all anime data from database"""
        conn = connect_to_db()
        query = "SELECT * FROM anime_data.anime WHERE content_string IS NOT NULL AND content_string != '';"
        df = pd.read_sql(query, conn)
        close_connection(conn)
        return df

    def get_user_high_rated_anime(self, user_id: int, min_rating: int = 7) -> list[int]:
        """Get user's high rated anime"""
        query = """
        SELECT anime_id 
        FROM anime_data.user_ratings 
        WHERE user_id = %s AND score >= %s
        """
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(query, (user_id, min_rating))
        results = [int(row[0]) for row in cursor.fetchall()]  # Convert to regular int
        close_connection(conn)
        return results

    def get_recommendations(self, user_id: int, x: int) -> list[int]:
        """Get recommendations for a user using cached data"""
        # Get user's high-rated anime
        liked_anime_ids = self.get_user_high_rated_anime(user_id)
        
        if not liked_anime_ids:
            print(f"User {user_id} has no high-rated anime. Returning popular anime...")
            return self._get_popular_anime(x)
        
        # Use cached data
        df = ContentFilter._anime_data
        cosine_sim = ContentFilter._cosine_sim
        indices = ContentFilter._indices
        
        # Calculate combined scores
        combined_scores = np.zeros(df.shape[0])
        for anime_id in liked_anime_ids:
            if anime_id in indices:
                idx = indices[anime_id]
                combined_scores += cosine_sim[idx]
        
        # Get top recommendations
        sim_scores = list(enumerate(combined_scores))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Filter out already rated anime and get top X
        liked_indices = {indices[aid] for aid in liked_anime_ids if aid in indices}
        recommended_indices = [i for i, score in sim_scores if i not in liked_indices][:x]
        
        # Convert numpy types to regular Python integers
        recommended_mal_ids = []
        for idx in recommended_indices:
            mal_id = df.iloc[idx]['mal_id']
            # Handle both numpy and pandas types
            if hasattr(mal_id, 'item'):
                recommended_mal_ids.append(int(mal_id.item()))
            else:
                recommended_mal_ids.append(int(mal_id))
        
        return recommended_mal_ids

    def _get_popular_anime(self, x: int) -> list[int]:
        """Fallback: return popular anime when user has no ratings"""
        query = """
        SELECT mal_id 
        FROM anime_data.anime 
        WHERE score IS NOT NULL 
        ORDER BY score DESC, popularity ASC 
        LIMIT %s
        """
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(query, (x,))
        results = [int(row[0]) for row in cursor.fetchall()]  # Convert to regular int
        close_connection(conn)
        return results

    @classmethod
    def clear_cache(cls):
        """Clear the cached data and remove cache file"""
        cls._anime_data = None
        cls._cosine_sim = None
        cls._indices = None
        if os.path.exists(cls._cache_file):
            os.remove(cls._cache_file)
            print("Cache cleared!")

    @classmethod
    def refresh_cache(cls):
        """Force recompute and cache the data"""
        cls.clear_cache()
        # Create dummy instance to trigger recompute
        dummy = ContentFilter(user_id=1)
        print("Cache refreshed!")