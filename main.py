# Import necessary libraries
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load data
movies = pd.read_csv('Dataset/movies.csv')
ratings = pd.read_csv('Dataset/ratings.csv')

# Merge data
data = pd.merge(ratings, movies, on='movieId')

# Create a pivot table
ratings_matrix = data.pivot_table(index='userId', columns='title', values='rating')


# Define a function to recommend movies
def recommend_movies(genre1, genre2):
    # Get movies that match both genre preferences
    genre1_movies = list(movies[movies['genres'].str.contains(genre1)]['title'])
    genre2_movies = list(movies[movies['genres'].str.contains(genre2)]['title'])
    common_movies = list(set(genre1_movies).intersection(set(genre2_movies)))

    # Compute cosine similarity between movies
    movie_similarity = cosine_similarity(ratings_matrix[common_movies].fillna(0).T)

    # Get movie recommendations
    recommendations = []
    for i, movie in enumerate(common_movies):
        index = movies[movies['title'] == movie].index[0]
        distances = movie_similarity[i]
        similar_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        for j, similar_movie in enumerate(similar_movies):
            recommendations.append((movies.iloc[similar_movie[0]].title, similar_movie[1]))

    # Sort recommendations by similarity score
    recommendations = sorted(recommendations, reverse=True, key=lambda x: x[1])

    # Print recommendations
    print(f"Top 5 movie recommendations for users who like {genre1} and {genre2}:")
    for i, recommendation in enumerate(recommendations[:5]):
        print(f"{i + 1}: {recommendation[0]} (Similarity Score: {recommendation[1]})")


# Test the recommendation system
recommend_movies('Action', 'Adventure')
