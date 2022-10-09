import mimetypes
from app import app, db
from flask import render_template, redirect, url_for, flash, Response, request, send_file

# from app.controller.recog.recog_utils import gen
from app.model.forms import EditUserPassword, LoginForm, SignUpForm, MissingPersonForm, EditUserForm, EditMissingPerson
from app.model.tables import User, bcrypt, Images, MissingPeople
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.controller.recog.get_missing_people import get_missing_people
from PIL import Image
import io



@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()

        if user and user.verify_password(form.password.data):
            if form.remember_me.data:
                login_user(user, remember=True)
            else:
                login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Check your credentials and try again")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():


        users_like_yours = User.query.filter_by(email=form.email.data).first()

        if users_like_yours is not None:
            flash("There is already an user with this email")
            return redirect(url_for('signup'))
        else:

            if form.photo.data is not None:
                pic = form.photo.data
                filename = secure_filename(pic.filename)
                mimetype = pic.mimetype
                print(mimetype)
                image = Images(picture=pic.read(), isUserProfile=True, isMissingPersonProfile=False, filename=filename,
                               mimetype=mimetype)
                hash_password = bcrypt.generate_password_hash(form.password.data.encode('utf8'))
                user = User(name=form.name.data, email=form.email.data,
                            password_hash=hash_password.decode('utf8'), profile_pic=image)

                db.session.add(user)
                db.session.add(image)
                db.session.commit()
                print("Usuário com imagem")
            else:
                hash_password = bcrypt.generate_password_hash(form.password.data.encode('utf8'))
                user = User(name=form.name.data, email=form.email.data,
                            password_hash=hash_password.decode('utf8'))
                db.session.add(user)
                db.session.commit()
                print("Usuário sem imagem")

            return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/insert_missing_person', methods=['POST'])
@login_required
def insert_missing_person():
    name = request.form.get('name')
    birthday = request.form.get('birthday')
    birthplace = request.form.get('birthplace')
    place_of_disappearance = request.form.get('place_of_disappearance')
    disappearance_details = request.form.get('disappearance_details')
    pic = request.files.get('pic')
    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    user = current_user
    user_id = user.id
    print(user_id)
    image = Images(picture=pic.read(), isUserProfile=False, isMissingPersonProfile=True, filename=filename,
                   mimetype=mimetype)

    missing_person = MissingPeople(user_id=user_id,name=name,birthday=birthday, birthplace=birthplace,
                                   place_of_disappearance=place_of_disappearance,
                                   disappearance_details=disappearance_details, pics=[image])

    db.session.add(missing_person)
    db.session.add(image)
    db.session.commit()
    return "ok"


@app.route('/login-app', methods=['POST'])
def login_app():
    email = request.json['email']
    print(email)
    user = User.query.filter_by(email=request.json['email']).first()

    if user and user.verify_password(request.json['password']):
        login_user(user)
        return "Login successful"
    else:
        return "Check your credentials and try again"


# @app.route('/video_feed')
# @login_required
# def video_feed():
#     get_missing_people()
#     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/user_image')
@login_required
def user_image():
    pic = Image.open(io.BytesIO(current_user.profile_pic.picture))
    img_io = io.BytesIO()
    mimetype = current_user.profile_pic.mimetype.split('/')
    pic.save(img_io, mimetype[1].upper(), quality=70)
    img_io.seek(0)
    return send_file(img_io, current_user.profile_pic.mimetype)

@app.route('/missing_people')
@login_required
def missing_people():
    missing_people = MissingPeople.query.all()
    return render_template('missing_people.html', missing_people=missing_people)


@app.route('/missing_person_images/<int:id>')
@login_required
def get_missing_person_images(id):
    image = Images.query.filter_by(missing_person_id=id).first()
    
    pic = Image.open(io.BytesIO(image.picture))
    img_io = io.BytesIO()
    mimetype = current_user.profile_pic.mimetype.split('/')
    pic.save(img_io, mimetype[1].upper(), quality=70)
    img_io.seek(0)
    return send_file(img_io, current_user.profile_pic.mimetype)


@app.route('/missing_person/<int:id>')
@login_required
def get_missing_person(id):
    missing_person = MissingPeople.query.filter_by(id=id).first()
    form = EditMissingPerson(
        name=missing_person.name, 
        birthday=missing_person.birthday,
        birthplace=missing_person.birthplace,
        place_of_disappearance=missing_person.place_of_disappearance,
        disappearance_details=missing_person.disappearance_details
    )
   
    return render_template("missing_person.html", missing_person=missing_person, form=form, id=id)

@app.route('/update_missing_person/<int:id>', methods=['POST'])
@login_required
def update_missing_person(id):
    form = EditMissingPerson()
    missing_person = MissingPeople.query.filter_by(id=id).first()
    if form.validate_on_submit():
            if form.photo.data == None:
                missing_person.name = form.name.data
                missing_person.birthday = form.birthday.data
                missing_person.birthplace = form.birthplace.data
                missing_person.place_of_disappearance = form.place_of_disappearance.data
                missing_person.disappearance_details = form.disappearance_details.data
                db.session.commit()
            else:
                pics_list = missing_person.pics
                
                pic = form.photo.data
                pics_list[0].picture = pic.read()
                pics_list[0].filename = secure_filename(pic.filename)
                pics_list[0].mimetype = pic.mimetype
                missing_person.name = form.name.data
                missing_person.birthday = form.birthday.data
                missing_person.birthplace = form.birthplace.data
                missing_person.place_of_disappearance = form.place_of_disappearance.data
                missing_person.disappearance_details = form.disappearance_details.data
                db.session.commit()
            return redirect(url_for('missing_people'))
    flash('form, not valid')        
    return redirect(url_for('missing_people'))

@app.route('/add_missing_person', methods=['GET', 'POST'])
@login_required
def add_missing_person():
    form = MissingPersonForm()
    if request.method =='GET':
        return render_template("add_missing_person.html", form=form)
    else:
        if form.validate_on_submit():
            
            user_id = current_user.id
            name = form.name.data
            birthday = form.birthday.data
            birthplace = form.birthplace.data
            place_of_disappearance = form.place_of_disappearance.data
            disappearance_details = form.disappearance_details.data
            pic = form.photo.data
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype
            image = Images(picture=pic.read(), isUserProfile=False, isMissingPersonProfile=True, filename=filename,
                   mimetype=mimetype)

            missing_person = MissingPeople(
                user_id=user_id,
                name=name,
                birthday=birthday,
                birthplace=birthplace, 
                place_of_disappearance=place_of_disappearance,
                disappearance_details=disappearance_details,
                pics=[image])
            
            db.session.add(image)
            db.session.add(missing_person)
            db.session.commit()
            return redirect(url_for("missing_people"))


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    
    if request.method == 'GET':
        form = EditUserForm(
        name=current_user.name,
        email=current_user.email
    )
        return render_template('edit_user.html', form=form)
    if request.method == 'POST':
        form = EditUserForm()
        user = current_user
        if form.validate_on_submit():
            if form.photo.data == None:
                user.name = form.name.data
                user.email = form.email.data
                db.session.commit()
            else:
                pic_row = current_user.profile_pic
                
                pic = form.photo.data
                pic_row.picture = pic.read()
                pic_row.filename = secure_filename(pic.filename)
                pic_row.mimetype = pic.mimetype
                user.name = form.name.data
                user.email = form.email.data
                db.session.commit()
            return redirect(url_for('home'))     
        
        return 'Bad request',404
    return 'Bad request',404    

@app.route('/edit_user/password', methods=['GET', 'POST'])
@login_required
def edit_user_password():
    form = EditUserPassword()
    if request.method == 'POST':
        if current_user.verify_password(form.current_password.data):
            password_hash = bcrypt.generate_password_hash(
                form.new_password.data.encode('utf8')
            )
            current_user.password_hash = password_hash.decode('utf8')
            db.session.commit()
            return render_template('index.html')
        else:
            flash('Check the current password and try again')
            return render_template('edit_user_password.html', form=form)    
    else:

        return render_template('edit_user_password.html', form=form)


@app.route('/delete_missing_person/<int:id>')
@login_required
def delete_missing_person(id):
    missing_person = MissingPeople.query.filter_by(id=id).first()
    db.session.delete(missing_person)
    db.session.commit()
    return redirect(url_for('missing_people'))

@app.route('/delete_user/')
@login_required
def delete_user():
    db.session.delete(current_user)
    db.session.commit()
    return redirect(url_for('home'))


