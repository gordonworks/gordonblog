from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
import re
from slugify import slugify
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import func

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(64), index=True, unique=True)
	body = db.Column(db.Text)
	
	tag_objects = db.relationship("Tag", secondary="post_tag")
	tags = association_proxy("tag_objects", "name",
								creator=lambda name: Tag(name=name))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.title)
	"""
	@hybrid_property
	def slug(self):
		result = []
		punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
		for word in punct_re.split(self.title.lower()):
			if word:
				result.append(word)
		return '-'.join(result)
	
	@slug.expression
	def slug(cls):
		result = []
		print(cls.title)
		punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
		for word in punct_re.split(cls.title):
			if word:
				result.append(word)
		return func.lower('-'.join(result))
	"""

	@hybrid_property
	def slug(self):
		return self.title.replace(" ", "-").lower()

	@slug.expression
	def slug(cls):
		return func.lower(func.replace(cls.title, " ", "-"))


class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Unicode, unique=True)

	def __repr__(self):
		return '<Tag {}>'.format(self.name)


post_tag = db.Table("post_tag",
	db.Column("post_id", db.ForeignKey("post.id"), primary_key=True),
	db.Column("tag_id", db.ForeignKey("tag.id"), primary_key=True))