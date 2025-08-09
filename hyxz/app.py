from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///huayangxianzhi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 管理员模型
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# 章节模型
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    translation = db.Column(db.Text, nullable=False)
    annotations = db.Column(db.Text)
    image_path = db.Column(db.String(300))

# 初始化数据库
with app.app_context():
    db.create_all()
    # 创建默认管理员账户
    if not Admin.query.filter_by(username='llh').first():
        admin = Admin(username='llh', password=generate_password_hash('127127'))
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    chapters = Chapter.query.all()
    return render_template('index.html', chapters=chapters)

@app.route('/add_chapter', methods=['GET', 'POST'])
def add_chapter():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # 处理表单提交
        title = request.form['title']
        original_text = request.form['original_text']
        translation = request.form['translation']
        annotations = request.form.get('annotations', '')
        
        new_chapter = Chapter(
            title=title,
            original_text=original_text,
            translation=translation,
            annotations=annotations
        )
        
        # Handle image upload
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"chapter_{int(time.time())}.{file.filename.split('.')[-1]}"
            file.save(os.path.join(upload_folder, filename))
            new_chapter.image_path = os.path.join('uploads', filename)
        
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin'))
    
    # 处理GET请求（显示表单）
    return render_template('add_chapter.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    chapters = Chapter.query.all()
    return render_template('admin.html', chapters=chapters)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        chapter.title = request.form['title']
        chapter.original_text = request.form['original_text']
        chapter.translation = request.form['translation']
        chapter.annotations = request.form['annotations']
        
        # Handle image upload if new image is provided
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"chapter_{chapter_id}.{file.filename.split('.')[-1]}"
            file.save(os.path.join(upload_folder, filename))
            chapter.image_path = os.path.join('uploads', filename)
        
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin'))
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        chapter.title = request.form['title']
        chapter.original_text = request.form['original_text']
        chapter.translation = request.form['translation']
        chapter.annotations = request.form['annotations']
        
        # Handle image upload if new image is provided
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"chapter_{chapter_id}.{file.filename.split('.')[-1]}"
            file.save(os.path.join(upload_folder, filename))
            chapter.image_path = os.path.join('uploads', filename)
        
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/get_chapter/<int:chapter_id>')
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return jsonify({
        'title': chapter.title,
        'original_text': chapter.original_text,
        'translation': chapter.translation,
        'annotations': chapter.annotations,
        'image_path': chapter.image_path
    })

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"img_{int(time.time())}.{file.filename.split('.')[-1]}"
        file.save(os.path.join(upload_folder, filename))
        return jsonify({'location': f"/static/uploads/{filename}"})



if __name__ == '__main__':
    app.run(debug=True)