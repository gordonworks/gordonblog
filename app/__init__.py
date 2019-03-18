from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager,current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditor, CKEditorField



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
ckeditor = CKEditor(app)

#app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
class GordonBlogModelView(ModelView):

	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self, name, **kwargs):
		# redirect to login page if user doesn't have access
		return redirect(url_for('index'))
	
	form_overrides = dict(body=CKEditorField)
	can_view_details = True
	create_template = 'edit.html'
	edit_template = 'edit.html'


admin = Admin(app, name='gordonblog', template_mode='bootstrap3')

from app import routes, models
from app.models import User,Post


admin.add_view(GordonBlogModelView(User, db.session))
admin.add_view(GordonBlogModelView(Post, db.session))