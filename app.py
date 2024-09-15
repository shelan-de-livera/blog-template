import os
from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')  # Securely retrieve the secret key from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///self_help_blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

google_bp = make_google_blueprint(
    client_id=os.environ.get('GOOGLE_CLIENT_ID'), 
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'), 
    redirect_to='google_login'
)
app.register_blueprint(google_bp, url_prefix='/login')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    articles = db.relationship('Article', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    likes = db.relationship('Like', backref='comment', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    email = resp.json()['emails'][0]['value']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
    return f'You are logged in as {email}'

@app.route('/articles')
def articles():
    articles = Article.query.all()
    return render_template('articles.html', articles=articles)

@app.route('/articles/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article_detail.html', article=article)

@app.route('/articles/<int:article_id>/comment', methods=['POST'])
def add_comment(article_id):
    content = request.form.get('content')
    # Note: Replace the following line with actual logged-in user logic
    user = User.query.first()  # Example: Get the first user (for testing purposes)
    comment = Comment(content=content, user_id=user.id, article_id=article_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('article_detail', article_id=article_id))

@app.route('/comments/<int:comment_id>/like')
def like_comment(comment_id):
    # Note: Replace the following line with actual logged-in user logic
    user = User.query.first()  # Example: Get the first user (for testing purposes)
    like = Like(user_id=user.id, comment_id=comment_id)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('articles'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)