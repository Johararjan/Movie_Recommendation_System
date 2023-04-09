# Import necessary libraries
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, render_template
import mysql.connector


# Load data
movies = pd.read_csv('Dataset/movies.csv')
ratings = pd.read_csv('Dataset/ratings.csv')

# Merge data
data = pd.merge(ratings, movies, on='movieId')

# Create a pivot table
ratings_matrix = data.pivot_table(index='userId', columns='title', values='rating')

# Define a Flask app
app = Flask(__name__)
@app.route('/contact-us', methods=['POST'])
def contact_us():
    # Get contact form data
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    # Create a connection to the MySQL database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Arjan196",
        database="movierecommend"
    )

    # Create a cursor to execute SQL queries
    cursor = db.cursor()

    # Define the SQL query to insert contact form data
    sql = "INSERT INTO contacts (name, email, subject, message) VALUES (%s, %s, %s, %s)"

    # Execute the query with the data
    values = (name, email, subject, message)
    cursor.execute(sql, values)

    # Commit the changes to the database
    db.commit()

    # Close the database connection and cursor
    cursor.close()
    db.close()

    return """
                <script>alert("Thank you for your message! We will get back to you soon."); 
                window.location.href = '/';</script>
                """
# Define a route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Define a route for the recommendation page
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/recommendation', methods=['POST'])
def recommendation():
    # Get genre preferences from the form
    genre1 = request.form['genre1']
    genre2 = request.form['genre2']

    # Get movies that match both genre preferences
    genre1_movies = set(movies[movies['genres'].str.contains(genre1)]['title'])
    genre2_movies = set(movies[movies['genres'].str.contains(genre2)]['title'])
    common_movies = list(genre1_movies.intersection(genre2_movies))

    # Check if common_movies is not empty
    if not common_movies:
        return render_template('no_movies.html')

    # Compute cosine similarity between movies
    common_movies = list(set(common_movies).intersection(
        ratings_matrix.columns))  # keep only movies that are present in the ratings_matrix
    common_ratings_matrix = ratings_matrix[common_movies].fillna(0)
    movie_similarity = cosine_similarity(common_ratings_matrix.T)

    # Get movie recommendations
    recommendations = []
    for i, movie in enumerate(common_movies):
        distances = movie_similarity[i]
        similar_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        for j, similar_movie in enumerate(similar_movies):
            recommendations.append((similar_movie[0], similar_movie[1]))

    # Sort recommendations by similarity score
    recommendations = sorted(recommendations, reverse=True, key=lambda x: x[1])

    # Get movie titles from their indices
    movie_indices = [r[0] for r in recommendations[:5]]
    movie_titles = [movies.iloc[idx]['title'] for idx in movie_indices]

    # Print the top 5 recommended movies
    print("Top 5 recommended movies:")
    for i, title in enumerate(movie_titles):
        print(f"{i + 1}. {title}")

    # Render the recommendation page with the recommendations
    return render_template('Recommendation.html', genre1=genre1, genre2=genre2, recommendations=movie_titles)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
