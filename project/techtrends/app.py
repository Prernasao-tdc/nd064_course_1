import sqlite3
import logging
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from datetime import datetime

# Initialize the connection count
db_connection_count = 0

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get a database connection.
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    # Log the new connection
    logging.debug(f'New database connection established. Total connections: {db_connection_count}')
    return connection

# Function to get a post using its ID
def get_post(post_id):
    with get_db_connection() as connection:
        post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the health check endpoint
@app.route('/healthz', methods=['GET'])
def health_check():
    logging.info('Health check endpoint accessed')
    return jsonify(result="OK - healthy"), 200

# Define the main route of the web application
@app.route('/')
def index():
    logging.info('Main page accessed')
    with get_db_connection() as connection:
        posts = connection.execute('SELECT * FROM posts').fetchall()
    return render_template('index.html', posts=posts)

@app.route('/metrics', methods=['GET'])
def metrics():
    with get_db_connection() as connection:
        post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]

    return jsonify(db_connection_count=db_connection_count, post_count=post_count), 200

# Define how each individual article is rendered
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.warning(f'Post with id {post_id} not found. Returning 404 page.')
        return render_template('404.html'), 404
    else:
        logging.info(f'Article "{post["title"]}" retrieved')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('About Us page accessed')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
            logging.error('Attempted to create a post without title')
        else:
            with get_db_connection() as connection:
                connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
                connection.commit()
            logging.info(f'New article "{title}" created')
            return redirect(url_for('index'))
    return render_template('create.html')

# Start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111)