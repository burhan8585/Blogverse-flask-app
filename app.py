from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect  # For form security
from models import db, Post, Category, Tag, User  # User for login
from forms import PostForm, LoginForm  , RegisterForm
from datetime import datetime
from urllib.parse import urlparse, urljoin
import os
import re
from flask_frozen import Freezer    

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')  # Fallback for local 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    search_query = request.args.get('q')
    
    query = Post.query.filter_by(published=True)
    
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        query = query.filter(Post.tags.contains(tag))
    
    if search_query:
        query = query.filter(
            db.or_(
                Post.title.contains(search_query),
                Post.content.contains(search_query),
                Post.excerpt.contains(search_query)
            )
        )
    
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    featured_posts = Post.query.filter_by(published=True, featured=True).order_by(Post.created_at.desc()).limit(3).all()
    categories = Category.query.all()
    
    return render_template('index.html', 
                         posts=posts, 
                         featured_posts=featured_posts,
                         categories=categories,
                         current_category=category_slug,
                         current_tag=tag_slug,
                         search_query=search_query)

@app.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    related_posts = Post.query.filter(
        Post.category_id == post.category_id,
        Post.id != post.id,
        Post.published == True
    ).order_by(Post.created_at.desc()).limit(3).all()
    categories = Category.query.all()
    
    return render_template('post_detail.html', post=post, related_posts=related_posts, categories=categories)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    categories = Category.query.all()
    
    if form.validate_on_submit():
        slug = slugify(form.title.data)
        base_slug = slug
        counter = 1
        while Post.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        post = Post(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            excerpt=form.excerpt.data,
            author=form.author.data,
            image_url=form.image_url.data,
            category_id=form.category_id.data,
            featured=form.featured.data,
            published=form.published.data
        )
        
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag_slug = slugify(tag_name)
                tag = Tag.query.filter_by(slug=tag_slug).first()
                if not tag:
                    tag = Tag(name=tag_name, slug=tag_slug)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('post_detail', slug=post.slug))
    
    return render_template('post_form.html', form=form, categories=categories, title='Create New Post')
# grok register code    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    categories = Category.query.all()  # For nav/sidebar if your templates use it
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)  # Auto-login after signup
        flash('Welcome! Account created successfully.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html', form=form, categories=categories)
# grok register code 
@app.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = PostForm(obj=post)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    categories = Category.query.all()
    
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.author = form.author.data
        post.image_url = form.image_url.data
        post.category_id = form.category_id.data
        post.featured = form.featured.data
        post.published = form.published.data
        post.updated_at = datetime.utcnow()
        
        post.tags.clear()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag_slug = slugify(tag_name)
                tag = Tag.query.filter_by(slug=tag_slug).first()
                if not tag:
                    tag = Tag(name=tag_name, slug=tag_slug)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('post_detail', slug=post.slug))
    
    return render_template('post_form.html', form=form, categories=categories, post=post, title='Edit Post')

@app.route('/post/<slug>/delete', methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/category/<slug>')
def category_posts(slug):
    return redirect(url_for('index', category=slug))

@app.route('/tag/<slug>')
def tag_posts(slug):
    return redirect(url_for('index', tag=slug))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    categories = Category.query.all()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form, categories=categories)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
#     app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)  # Auto-reload magic here 


# For freezing (run separately)
if __name__ == '__freeze':
    freezer.freeze()  # Generates static files