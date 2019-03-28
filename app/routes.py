from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Post
from werkzeug.urls import url_parse

@app.context_processor
def tags_dict():
	tags = {}
	for p in Post.query.all():
		if p.tags:
			for t in p.tags.split(','):
				tags[t] = tags.get(t,0)+1
	return tags

@app.route('/')
@app.route('/index')
def index():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(page,app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('index', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Home',
						   posts=posts.items, next_url=next_url,
						   prev_url=prev_url,tags=tags_dict())

@app.route('/index/<tag>')
def taggedindex(tag):
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter(Post.tags.like(f'%{tag}%')).order_by(
							Post.timestamp.desc()).paginate(page,app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('index', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Home',
						   posts=posts.items, next_url=next_url,
						   prev_url=prev_url,tags=tags_dict())


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/<int:year>/<int:month>/<int:day>/<slug>')
def fullpost(year,month,day,slug):
	post = Post.query.filter_by(slug=slug).first()
	return render_template('post.html', title='View Posts', post=post)