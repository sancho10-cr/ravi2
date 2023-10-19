from flask import ( Flask, 
            jsonify, request, 
            after_this_request, json, 
            render_template, redirect, 
            url_for, abort, make_response, flash)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_required,login_user,logout_user,LoginManager,UserMixin,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import Signin,Signup
import numpy as np
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['course_per_page']=6
app.config['SECRET_KEY']='THISISMYSUPERSECRETKEY'
db = SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


categories = db.Table('categories_table',
    db.Column('categories_id', db.Integer, db.ForeignKey(
        'categories.id'), primary_key=True),
    db.Column('courses_id', db.Integer, db.ForeignKey(
        'courses.id'), primary_key=True)
)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

 
class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.DateTime,nullable=False,default=datetime.now)
    title = db.Column(db.String(500), nullable=False, unique=True)
    subtitle = db.Column(db.String(500))
    page_url = db.Column(db.String(500), nullable=False, unique=True)
    requirements = db.Column(db.Text)
    description = db.Column(db.Text)
    course_for=db.Column(db.Text)
    image=db.Column(db.String(100),nullable=False)
    # categories=db.relationship('Categories',backref='courses')
    author_id = db.Column(db.Integer, db.ForeignKey(
        'author.id'), nullable=False)
    # Initially lazy='subquery'
    categories = db.relationship('Categories', secondary=categories, lazy='dynamic',
        backref=db.backref('courses', lazy=True))


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Courses', backref='author')

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class UserCourses(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    course_id=db.Column(db.Integer,nullable=False)

class RecommendationTable(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    course_id=db.Column(db.Integer,nullable=False)
    recom_course_id1=db.Column(db.Integer,nullable=False)
    recom_course_id2=db.Column(db.Integer,nullable=False)
    recom_course_id3=db.Column(db.Integer,nullable=False)
    recom_course_id4=db.Column(db.Integer,nullable=False)
    recom_course_id5=db.Column(db.Integer,nullable=False)

class RecommendationScoreTable(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    course_id=db.Column(db.Integer,nullable=False)
    recom_score_id1=db.Column(db.Float,nullable=False)
    recom_score_id2=db.Column(db.Float,nullable=False)
    recom_score_id3=db.Column(db.Float,nullable=False)
    recom_score_id4=db.Column(db.Float,nullable=False)
    recom_score_id5=db.Column(db.Float,nullable=False)
    
# db.create_all()
# admin = Admin(app, name='E-Learning System', template_mode='bootstrap4')
# admin.add_view(ModelView(Courses, db.session))
# admin.add_view(ModelView(Author, db.session))
# admin.add_view(ModelView(Categories,db.session))
# admin.add_view(ModelView(categories,db.session))

def get_user_course_list():
    course_id_list=[]
    if current_user.is_authenticated:
        user_id=current_user.id
        user_courses_ids=UserCourses.query.filter_by(user_id=user_id).all()
        for course_id in user_courses_ids:
            course_id_list.append(course_id.course_id)
    return course_id_list


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        referrer=request.referrer
        # login code goes here
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(email=username).first()
        if not user or not check_password_hash(user.password,password):
            flash('Either Email address or password is incorrect')
            return render_template('login.html')
        login_user(user)
        if 'login' in referrer:
            return redirect(url_for('home'))
        else:
            return redirect(referrer)
    return render_template('login.html')

@app.route('/logout')
def logout():
    # referrer=request.referrer
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup',methods=['POST'])
def signup():
    referrer = request.referrer
    # code to validate and add user to database goes here
    email = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    if password!=confirm_password:
        flash('Password and confirm_password mismatch')
        return redirect(referrer)

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email already exists')
        return redirect(referrer)

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(referrer)

@app.route('/buy_course')
@login_required
def buy_course():
    referrer=request.referrer
    course_id=request.args.get('course_id')
    user_id=current_user.id
    if course_id:
        course_id=int(course_id)
    has_course=UserCourses.query.filter_by(course_id=course_id,user_id=user_id).first()
    if not has_course:
        data_to_db=UserCourses(course_id=course_id,user_id=user_id)
        db.session.add(data_to_db)
        db.session.commit()
    return redirect(referrer)

@app.route('/get_user_courses')
@login_required
def get_user_courses():
    course_id_list=get_user_course_list()
    recom_score_list=[]
    recom_course_list=[]
    for course_id in course_id_list:
        recom_score=RecommendationScoreTable.query.filter_by(course_id=course_id).first()
        recom_course=RecommendationTable.query.filter_by(course_id=course_id).first()
        temp_recom_score=[
                        recom_score.recom_score_id1,recom_score.recom_score_id2,
                        recom_score.recom_score_id3,recom_score.recom_score_id4,
                        recom_score.recom_score_id5
                        ]
        print(f'Recom Score:{temp_recom_score}')
        temp_recom_course=[
                        recom_course.recom_course_id1,recom_course.recom_course_id2,
                        recom_course.recom_course_id3,recom_course.recom_course_id4,
                        recom_course.recom_course_id5
                            ]
        recom_score_list.extend(temp_recom_score)
        recom_course_list.extend(temp_recom_course)
    recom_score_list=np.array(recom_score_list)
    recom_course_list=np.array(recom_course_list)
    recom_score_idx=np.argsort(recom_score_list)
    recom_score_list.sort()
    recom_course_idx=recom_course_list[recom_score_idx[::-1]]
    filtered_course_ids=[]
    for recom_course_id in recom_course_idx:
        if recom_course_id not in filtered_course_ids:
            if recom_course_id not in course_id_list:
                filtered_course_ids.append(int(recom_course_id))
    
    recommended_courses=[]
    count=3
    for recom_id in filtered_course_ids:
        print(f'Recom Id:{recom_id}')
        temp_data=Courses.query.filter_by(id=recom_id).first()
        if count==7:
            ext='.png'
            count=3
        else:
            ext='.jpg'
        img_data='e-learning'+str(count)+ext
        recommended_courses.append((temp_data,img_data))
        count+=1
    # recom_score=RecommendationScoreTable.query.filter(RecommendationScoreTable.course_id.in_(course_id_list)).all()
    print(recom_score_list[-4:],recom_score_idx[-4:],filtered_course_ids)
    print(recommended_courses)
    recommended_courses_side=recommended_courses[:5]
    if len(recommended_courses)>10:
        recommended_courses_bottom=recommended_courses[5:10]
    else:
        recommended_courses_bottom=recommended_courses[5:]
    courses=Courses.query.filter(Courses.id.in_(course_id_list)).all()
    print(f'Course ID List:{course_id_list}')
    title=f"Your Courses"
    return render_template('user_courses.html',
                            courses=courses,title=title,
                            user_course_list=course_id_list,
                            author_courses=[],
                            recommended_courses_side=recommended_courses_side,
                            recommended_courses_bottom=recommended_courses_bottom)

@app.route('/add_course',methods=['GET','POST'])
@login_required
def add_course():
    if not current_user.name=='admin':
        abort(404)
    # @after_this_request
    # def add_header(response):
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     return response

    if request.method=='POST':
        data=json.loads(request.data)
        categories=data['categories']
        data['categories']=[]
        # Add categories into the database
        for category in categories:
            category=category.lower().strip()
            category_db=Categories.query.filter_by(name=category).first()
            if not category_db:
                category_db=Categories(name=category)
                db.session.add(category_db)
                db.session.commit()
            data['categories'].append(category_db)
            db.session.add(category_db)
            db.session.commit()
        author=data['author']
        # Convert author into lower case
        author=author.lower().strip()
        # Get author
        author_db=Author.query.filter_by(name=author).first()
        if not author_db:
            author_db=Author(name=author)
            db.session.add(author_db)
            db.session.commit()

        data['author']=author_db
        # Get details of total data stored in the database
        data_in_db=Courses.query.all()
        if not data_in_db:
            data['image']='image1'
        else:
            data['image']='image'+str(len(data_in_db)+1)

        data_to_db=Courses(**data)
        db.session.add(data_to_db)
        db.session.commit()
        response=jsonify(Message="OK")
        response.headers.set('Access-Content-Allow-Origin','*')
        print('Data successfully written')
        return response,200
    response=make_response(render_template('add_course.html'))
    response.headers.set('Access-Content-Allow-Origin','*')
    return response

@app.route('/display/<page_url>')
def display(page_url):
    data=Courses.query.filter_by(page_url=page_url).first()
    course_id=data.id
    recom_data=RecommendationTable.query.filter_by(course_id=course_id).first()
    recom_course_ids=[]
    if recom_data:
        recom_course_ids=[
            recom_data.recom_course_id1,recom_data.recom_course_id2,
            recom_data.recom_course_id3,recom_data.recom_course_id4,
            recom_data.recom_course_id5
                        ]
    recommended_courses=[]
    count=3
    for recom_id in recom_course_ids:
        temp_data=Courses.query.filter_by(id=recom_id).first()
        if count==7:
            ext='.png'
        else:
            ext='.jpg'
        img_data='e-learning'+str(count)+ext
        recommended_courses.append((temp_data,img_data))
        count+=1

    print(recom_course_ids,recommended_courses)
    if not data:
        abort(404)
    author=data.author.name
    author_courses=Author.query.filter_by(name=author).first().courses
    author_filtered_courses=[]
    for author_course in author_courses:
        if page_url!=author_course.page_url:
            author_filtered_courses.append(author_course)
    if len(author_filtered_courses)>3:
        author_filtered_courses=author_filtered_courses[:3]
    user_course_list=get_user_course_list()
    return render_template('course.html',data=data,
                            author_courses=author_filtered_courses,
                            user_course_list=user_course_list,
                            recommended_courses=recommended_courses)

@app.route('/delete/<page_url>')
def delete(page_url):
    referrer = request.referrer
    print(f'Referrer:{referrer}')
    course=Courses.query.filter_by(page_url=page_url).first()
    print(course)
    course.categories=[]
    Courses.query.filter_by(page_url=page_url).delete()

    db.session.commit()
    return redirect(referrer)

# @app.route('/',methods=['GET','POST'])
# def display_urls():

#     courses=Courses.query.all()
#     return render_template('display_urls_cards.html',courses=courses[::-1],title="All Courses",subtitle=f"Total courses added:{len(courses)}")

# @app.route('/home_test',methods=['GET'],defaults={'page':1})
@app.route('/',methods=['GET'])
def home():
    page=request.args.get('page',1,type=int)
    courses=Courses.query.paginate(page,per_page=app.config['course_per_page'],error_out=False)
    if current_user.is_authenticated:
        user_id=current_user.id
        user_courses_ids=UserCourses.query.filter_by(user_id=user_id).all()
        user_course_list=[]
        for course_id in user_courses_ids:
            user_course_list.append(course_id.course_id)
        return render_template('home.html',courses=courses,title="All Courses",subtitle="Explore our unique courses",user_course_list=user_course_list)
    return render_template('home.html',courses=courses,title="All Courses",subtitle="Explore our unique courses")


@app.route('/categories/<categories>')
def categories(categories):
    page=request.args.get('page',1,type=int)
    courses=Categories.query.filter_by(name=categories).first().courses
    user_course_list=get_user_course_list()
    title=f"All Courses From {categories.title()} Categories"
    return render_template('display_urls_cards.html',
                            courses=courses,title=title,
                            url='categories',user_course_list=user_course_list)

@app.route('/author/<author>')
def author(author):
    user_course_list=[]
    courses=Author.query.filter_by(name=author).first().courses
    user_course_list=get_user_course_list()
    title=f"All Courses BY {author.title()}"
    return render_template('display_urls_cards.html',
                            courses=courses,title=title,
                            user_course_list=user_course_list)

@app.route('/profile')
def profile():
    courses=Author.query.filter_by(name=author).first().courses
    title=f"All Courses BY {author.title()}"
    return render_template('display_urls_cards.html',courses=courses,title=title)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__=='__main__':
    app.run(debug=True)