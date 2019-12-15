import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, Flask
from forum_isu import app, db, bcrypt
from forum_isu.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, AddCommentForm
from forum_isu.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask import jsonify
import json, datetime


@app.route('/')
@app.route('/home', methods=['GET','POST'])
def home():
    posts = Post.query.all()
    form = PostForm()
    formc = AddCommentForm()
    return render_template('home.html', title='Home',form=form, legend='Create Post', posts=posts, formc=formc)

@app.route('/addPost', methods=['POST'])
def addPost():
    print("in add post")
    form = PostForm()
    picture=None 
    if form.validate_on_submit():
        if form.picture.data:
           picture=save_picture(form.picture.data)
        post = Post(title=form.title.data, content=form.content.data, author=current_user, picture=picture)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))


@app.route('/addComment', methods=['POST'])
@login_required
def addComment():
    cText = request.form['comment_text']
    cPostId = request.form['comment_post_id']
    cUserId=request.form['comment_user_id']
    print("----->"+cText)
    print("----->"+cPostId)
    comment = Comment(comment=cText, user_id=cUserId,  post_id = cPostId)
    db.session.add(comment)
    db.session.commit()
    return jsonify(res="successxx")

    


@app.template_filter('getUser')
def getUser(userId):
    user=User.query.filter_by(id=userId).all()
    return user

@app.template_filter('getComments')
def getComments(postId):
    comments=Comment.query.filter_by(post_id=postId).all()
    return comments

@app.template_filter('getDisplayDate')
def getDisplayDate(d):
    return d.strftime("%c")

@app.route('/about')
def about():
    return render_template ('about.html', title = "About")

@app.route('/profile')
def profile():

    return render_template ('profile.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'account created for {form.username.data}!','success')
        return redirect(url_for('login'))

    return render_template ('register.html', title = "register", form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    print("hello...");
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            #return redirect(next_page) if next_page else redirect(url_for('home'))
            return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template ('login.html', title = "login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    posts= Post.query.filter_by(user_id=current_user.id)#.first()
    return render_template ('my_posts.html', title = "my_posts", posts=posts)

@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    print("entered update post")
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    print("recognized post form")
    if form.validate_on_submit():
        print("entered post form")
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        print("form is updated")
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        print("--------->form is get")
        form.title.data = post.title
        form.content.data = post.content
    print("--------->before render")
    return render_template('update_post.html', title='Update Post',
                           form=form, legend='Update Post', post_id=post_id)


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments=Comment.query.filter_by(post_id=post_id).all()
    if post.author != current_user:
        abort(403)
    for i in comments:
        db.session.delete(i)
        db.session.commit()
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('my_account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template ('my_account.html', title = "my_account", image_file=image_file, form=form)#, tempvar = arry_p)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn






    