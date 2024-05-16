import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import boto3


db_username = os.environ['DB_USERNAME']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']

aws_bucket_name = os.getenv('AWS_BUCKET_NAME')
aws_region = os.getenv('AWS_REGION')
picture_url = os.getenv('PIC_URL')


db_uri = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
print(f"Connecting db @{db_uri}")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)


s3_client = boto3.client('s3', region_name=aws_region)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Add password field

    def __init__(self, name, password):
        self.name = name
        self.password = password

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/users', methods=['POST'])
def add_user():
    try:
        request_data = request.form
        u_name = request_data['name']
        u_password = request_data['password']
        new_user = User(name=u_name, password=u_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('show_picture', picture_url=picture_url, user_name=u_name))

    except Exception as e:
        print("Error:", e)
        return "Internal Server Error", 500


@app.route('/users')
def show_users():
    users = User.query.all()
    user_list = {user.id: {'name': user.name, 'password': user.password} for user in users}
    return render_template('users.html', users=user_list)


@app.route("/show-picture")
def show_picture():
    # The key of the picture in the S3 bucket
    user_name = request.args.get('user_name')

    return render_template('show_picture.html', picture_url=picture_url, user_name=user_name)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)