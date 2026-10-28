from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint('posts', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
@bp.route('/<int:page>')
@bp.route('/<int:page>/<int:limit>')
def index(page=1, limit=20):
    if current_user.is_authenticated:
        return render_template('index.html', posts=current_user.posts)
    else:
        return render_template('index.html')

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if current_user.is_authenticated:
        if request.method == 'POST':
            post = Post(request.form['title'], request.form['content'], current_user)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('posts.index'))
        return render_template('add.html')
    else:
        return redirect(url_for('users.login'))

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get(id)
    if post.author != current_user:
        return redirect(url_for('posts.index'))
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('posts.index'))
    return render_template('edit.html', post=post)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    post = Post.query.get(id)
    if post.author != current_user:
        return redirect(url_for('posts.index'))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts.index'))