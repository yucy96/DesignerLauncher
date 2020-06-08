from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import config
from models import User, Material, Work, Sale, Size
from exts import db
# from decorators import login_required
from auth import SignupForm, LoginForm
from user import ChangeSettingForm, ProfileForm, identification_mapping, gender_mapping
import sys
from logging.config import dictConfig
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
import boto3
from botocore.exceptions import ClientError
import logging
import uuid
import utils
from sqlalchemy import func, and_, select


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
login_manager = LoginManager()


# def create_app():
app = Flask(__name__)
app.config.from_object(config)
app.secret_key = b'|{S\xfd\xfe\xde\xb7\x83\x16\xa6&U=\x90\xbe\xf8'
Bootstrap(app)
db.init_app(app)
CSRFProtect(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.init_app(app)
with app.app_context():
    db.create_all()
    # return app


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    app.logger.info('Current session: %s', user_id)
    if user_id is not None:
        return User.query.get(user_id)
    return None

# app = create_app()
@app.route('/')
@app.route('/index')
def index():
    app.logger.info('Session: %s', current_user)
    return render_template('index.html', user=current_user)


@app.route('/login', methods=['GET','POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect('/')  # Bypass if user is logged in
    form = LoginForm()
    if request.method == 'GET':
        return render_template('auth/sign_in.html',
                               form=form,
                               title='Log in.',
                               template='login-page',
                               body="Log in with your User account.", user=current_user)
    else:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()  # Validate Login Attempt
            if user and user.check_password(password=form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                app.logger.info('%s logged in successfully', user.id)
                return redirect(next_page or '/')
            flash('Invalid username/password combination')
            return redirect('/login')
        return render_template('auth/sign_in.html',
                               form=form,
                               title='Log in.',
                               template='login-page',
                               body="Log in with your User account.",
                               error='Invalid username/password combination', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('auth/sign_up.html',
                               title='Create an Account.',
                               form=form,
                               template='signup-page',
                               body="Sign up for a user account.", user=current_user)
    else:
        if form.validate_on_submit():
        # User sign-up logic will go here.
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user is None:
                user = User(first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            email=form.email.data)
                if user.generate_id() < 0:
                    flash('Create failure!')
                    return redirect('/register')
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()  # Create new user
                # TODO: login_user
                login_user(user)  # Log in as newly created user
                return redirect('/user_profile')  # TODO: templates/user/user_profile.html
            flash('A user already exists with that email address.')
        return render_template('auth/sign_up.html',
                               title='Create an Account.',
                               form=form,
                               template='signup-page',
                               body="Sign up for a user account.", user=current_user)


@app.route('/logout')
@login_required
def logout():
    app.logger.info('log out')
    logout_user()
    return redirect('/')


@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
# self profile
    form = ProfileForm(gender=current_user.gender, description=current_user.description)
    if request.method == 'GET':
        return render_template('user/user_profile.html', form=form, user=current_user, visitor=current_user)
    else:
        if form.validate_on_submit():
            user = current_user
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.gender = form.gender.data
            if form.birthday.data == 'None':
                user.birthday = None
            else:
                user.birthday = form.birthday.data
            user.position = form.position.data
            user.company_name = form.company.data
            user.description = form.description.data
            user.identification = form.identification.data
            db.session.add(user)
            db.session.commit()  # Create new user
            return redirect('/user_profile')
        app.logger.info("%s", form.errors)
        return render_template('user/user_profile.html', form=form, user=current_user, visitor=current_user)


@app.route('/user_profile/<user_id>', methods=['GET'])
@login_required
def see_profile(user_id):
    if user_id == current_user.id:
        return redirect('/user_profile')
    user = User.query.filter_by(id=user_id).first()
    print(user.gender, user.identification)
    if user.gender != None:
        user.gender = gender_mapping[user.gender][1]
    if user.identification != None:
        user.identification = identification_mapping[user.identification][1]
    return render_template('user/user_profile.html', user=user, visitor=current_user)


@app.route('/user_work', methods=['GET'])
@login_required
def my_work():
    user = current_user
    sql_tmp = select([Work.id, func.max(Work.phase).label('phase')]).group_by(Work.id).alias("sql_tmp")
    # print(sql_tmp)
    for_sale_works = db.session.query(Sale, Work).join(Work).filter(and_(Work.id==sql_tmp.c.id, Work.phase==sql_tmp.c.phase, Work.user_id==user.id, Work.for_sale==True)).all()
    non_sale_works = Work.query.filter(and_(Work.id==sql_tmp.c.id, Work.phase==sql_tmp.c.phase, Work.user_id==user.id, Work.for_sale==False)).all()
    print(for_sale_works[0][0].__dict__, for_sale_works[0][1].__dict__)
    print(non_sale_works)
    return render_template('user/personal_work.html', user=user, visitor=current_user, for_sale_works=for_sale_works, non_sale_works=non_sale_works)


@app.route('/user_work/<user_id>', methods=['GET'])
@login_required
def see_userwork(user_id):
    if user_id == current_user.id:
        return redirect('/user_work')
    else:
        user = User.query.get(user_id)
        print(user)
        sql_tmp = select([Work.id, func.max(Work.phase).label('phase')]).group_by(Work.id).alias("sql_tmp")
        print(sql_tmp)
        for_sale_works = db.session.query(Sale, Work).join(Work).filter(
            and_(Work.id == sql_tmp.c.id, Work.phase == sql_tmp.c.phase, Work.user_id == user.id,
                 Work.for_sale == True)).all()
        non_sale_works = Work.query.filter(
            and_(Work.id == sql_tmp.c.id, Work.phase == sql_tmp.c.phase, Work.user_id == user.id,
                 Work.for_sale == False)).all()
        print(for_sale_works[0][0].__dict__, for_sale_works[0][1].__dict__)
        print(non_sale_works)
        return render_template('user/personal_work.html', user=user, visitor=current_user, for_sale_works=for_sale_works,
                              non_sale_works=non_sale_works)


@app.route('/work/<work_id>/delete', methods=['POST'])
@login_required
def delete_work(work_id):
    print(work_id)
    works = Work.query.filter(Work.id==work_id).all()
    print(works)
    if works is None:
        flash("Work not found")
    for work in works:
        if work.user_id != current_user.id or work.for_sale: # Can't delete work if for sale
            flash("You can't delete this work!")
        else:
            Material.query.filter(Material.work_id == work_id).delete()
            Size.query.filter(Size.work_id == work_id).delete()
            # Sale.query.filter(Sale.work_id == work_id).delete()
            Work.query.filter(Work.id==work_id).delete()
            print("deleted!")
    db.session.commit()
    return redirect('/user_work')


@app.route('/mysettings', methods=['GET', 'POST'])
@login_required
def edit_settings():
    form = ChangeSettingForm()
    if request.method == 'GET':
        return render_template('user/change_password.html', form=form, user=current_user)
    else:
        if form.validate_on_submit():
            user = current_user
            if user and user.check_password(password=form.old_password.data):
                user.set_password(form.new_password.data)
                db.session.add(user)
                db.session.commit()

                app.logger.info('%s changed password successfully', user.id)
                return redirect('/user_profile')
            flash('Old password is wrong')
            return redirect('/mysettings')
        return render_template('user/change_password.html', form=form, user=current_user)


@app.route('/post_work', methods=['GET', 'POST'])
def post_work():
    if request.method == 'GET':
        return render_template('work/post_work1.html', user=current_user)
    else:
        s3_client = boto3.client('s3')
        work_id = uuid.uuid1()
        phase = request.form.get('phase')  # string
        print('phase', phase)
        work_name = request.form.get('work_name')
        gender = request.form.get('gender')
        category = request.form.get('category')
        design_style = request.form.get('design_style')

        # cover image part
        cover_image_name = request.form.get('cover_image')
        cover_image = request.files['cover_image']
        s3_client.upload_fileobj(
            cover_image,
            'design-phase-' + str(phase),
            current_user.id + '/' + str(work_id) + '/' + 'cover-image' + '/' + cover_image.filename,
        )
        cover_image_url = 'https://design-phase-' + str(phase) + '.s3.amazonaws.com/' + current_user.id + '/' + str(work_id) + '/' + 'cover-image' + '/' + cover_image.filename
        print('cover_imate', cover_image, cover_image_url)

        tags = request.form.get('tag').split(',')
        colors = request.form.get('color').split(',')

        # phase-1 pics part
        sketch_pics = None
        sketch_pics_url = []
        flat_pics = None
        flat_pics_url = []
        if phase == '1':
            sketch_pics = request.files.getlist('sketch_pic')
            for file in sketch_pics:
                s3_client.upload_fileobj(
                    file,
                    'design-phase-1',
                    current_user.id + '/' + str(work_id) + '/' + 'sketch-pic' + '/' + file.filename,
                )
                sketch_pics_url.append('https://design-phase-1.s3.amazonaws.com/' + current_user.id + '/' + str(work_id) + '/' + 'sketch-pic' + '/' + file.filename)
            print('sketch_pics', sketch_pics, sketch_pics_url)
            flat_pics = request.files.getlist('flat_pic')
            for file in flat_pics:
                s3_client.upload_fileobj(
                    file,
                    'design-phase-1',
                    current_user.id + '/' + str(work_id) + '/' + 'flat-pic' + '/' + file.filename,
                )
                flat_pics_url.append('https://design-phase-1.s3.amazonaws.com/' + current_user.id + '/' + str(work_id) + '/' + 'flat-pic' + '/' + file.filename)
            print('flat_pics', flat_pics, flat_pics_url)

        short_description = request.form.get('short_description')
        print('short_description', short_description)
        inspiration = request.form.get('inspiration')
        print('inspiration', inspiration)
        detail = request.form.get('detail')
        print('detail', detail)

        sale_id = uuid.uuid1()
        for_sale = utils.string_to_bool(request.form.get('for_sale'))
        print('for_sale', for_sale)

        phase2_expected_sale = None
        if phase == '1' and for_sale:
            phase2_expected_sale = request.form.get('phase2_expected_sale')
            print('phase2_expected_sale', phase2_expected_sale)

        # phase 2 picture part
        model_fit = None
        model_fit_urls = []
        if phase == '2':
            model_fit = request.files.getlist('p2_model_pic')
            for file in model_fit:
                s3_client.upload_fileobj(
                    file,
                    'design-phase-2',
                    current_user.id + '/' + str(work_id) + '/' + 'p2-model-pic' + '/' + file.filename,
                )
                model_fit_urls.append('https://design-phase-2.s3.amazonaws.com/' + current_user.id + '/' + str(work_id) + '/' + 'model-pic' + '/' + file.filename)
            print('p2_model_pics', model_fit, model_fit_urls)

        phase3_expected_sale = None
        expected_price = None
        if phase == '2' and for_sale:
            phase3_expected_sale = request.form.get('phase3_expected_sale')
            expected_price = request.form.get('expected_price')
            print('phase3_expected_sale', phase3_expected_sale, 'expected_price', expected_price)

        model_pics = None
        model_pics_url = []
        detail_pics = None
        detail_pics_url = []
        if phase == '3':
            model_pics = request.files.getlist('p3_model_pic')
            print('p3_model_pics', model_pics)
            for file in model_pics:
                s3_client.upload_fileobj(
                    file,
                    'design-phase-3',
                    current_user.id + '/' + str(work_id) + '/' + 'p3-model-pic' + '/' + file.filename,
                )
                model_pics_url.append('https://design-phase-3.s3.amazonaws.com/' + current_user.id + '/' + str(work_id) + '/' + 'p3-model-pic' + '/' + file.filename)
            print('p3_model_pics', model_pics, model_pics_url)

            detail_pics = request.files.getlist('p3_detail_pic')
            print('p3_detail_pics', detail_pics)
            for file in detail_pics:
                s3_client.upload_fileobj(
                    file,
                    'design-phase-3',
                    current_user.id + '/' + str(work_id) + '/' + 'p3-detail-pic' + '/' + file.filename,
                )
                detail_pics_url.append('https://design-phase-3.s3.amazonaws.com/' + current_user.id + '/' + str(
                    work_id) + '/' + 'p3-detail-pic' + '/' + file.filename)
            print('p3_detail_pics', detail_pics, detail_pics_url)

        final_price = None
        if phase == '3' and for_sale:
            final_price = request.form.get('final_price')
            print('final_price', final_price)

        # suppose that from here user will always create a new work
        sale = Sale(sale_id, phase2_expected_sale, expected_price, phase3_expected_sale, final_price)
        db.session.add(sale)
        db.session.commit()

        cur_work = Work(work_id, phase=int(phase), user_id=current_user.id, sale_id=sale_id, name=work_name,
                        short_description=short_description, for_sale=for_sale, gender=gender, category=category,
                        colors=colors, sketch_pic=sketch_pics_url, flat_pic=flat_pics_url, inspiration=inspiration,
                        details=detail, design_type=design_style, cover_image=cover_image_url, tags=tags,
                        model_fit=model_fit_urls, model_pics=model_pics_url, detail_pics=detail_pics_url)
        db.session.add(cur_work)
        db.session.commit()

        # add list to other fields
        # materials
        material_num = 0
        if phase == '2':
            material_num = request.form.get('material_num')
            for i in range(1, int(material_num) + 1):
                material_id = uuid.uuid1()
                part = request.form.get('part' + str(i))
                material = request.form.get('material_list' + str(i))
                material_color = request.form.get('color' + str(i))
                material_pic = request.files['material_pic' + str(i)]
                s3_client.upload_fileobj(
                    material_pic,
                    'designer-materials',
                    current_user.id + '/' + str(work_id) + '/' + 'material_pic' + str(i) + '/' + material_pic.filename,
                )
                pic_url = 'https://designer-materials.s3.amazonaws.com/' + current_user.id + '/' + str(
                    work_id) + '/' + 'material_pic' + str(i) + '/' + material_pic.filename
                cur_material = Material(material_id, name=material, pic=pic_url, part=part, color=material_color,
                                        work_id=work_id, phase=int(phase))
                db.session.add(cur_material)
                db.session.commit()
                print('material' + str(i), part, material, material_color, material_pic, pic_url)
            print('materials num', material_num)

        # sizes
        size_num = 0
        if phase == '3':
            size_num = request.form.get('size_num')
            for i in range(1, int(size_num) + 1):
                size_id = uuid.uuid1()
                size_type = request.form.get('size_type' + str(i))
                shoulder = request.form.get('shoulder' + str(i))
                bust = request.form.get('bust' + str(i))
                waist = request.form.get('waist' + str(i))
                hip = request.form.get('hip' + str(i))
                length = request.form.get('length' + str(i))
                width = request.form.get('width' + str(i))
                height = request.form.get('height' + str(i))
                cur_size = Size(size_id, size=size_type, shoulder=shoulder, bust=bust, waist=waist, hip=hip, length=length, width=width, height=height, work_id=work_id, phase=int(phase))
                db.session.add(cur_size)
                db.session.commit()
                print('size item', size_type, shoulder, bust, waist, hip, length, width, height, cur_size)
            print('size num', size_num)

        next_page = request.args.get('next')
        return redirect('/')


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    else:
        return {}
if __name__ == '__main__':
    app.run(debug=True)
