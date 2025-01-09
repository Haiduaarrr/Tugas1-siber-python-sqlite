from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

# Penambahan kode untuk nomer B.1
from flask import session
from functools import wraps

# Penambahan kode untuk nomer B.4
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# Penambahan kode untuk nomer B.1
# Konfigurasi session
app.config['SECRET_KEY'] = 'siswa123'
app.config['SESSION_TYPE'] = 'filesystem'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Penambahan kode untuk nomer B.1
# perubahan baru (penambahan @login_required )
@login_required 
@app.route('/')
def index():
    # RAW Query
    # students = db.session.execute(text('SELECT * FROM student')).fetchall()  # kode asli nya ini
    students =  Student.query.all()  # Pembaruan kode untuk nomer B.2. Menggunakan ORM SQLAlchemy
    return render_template('index.html', students=students)



@app.route('/add', methods=['POST'])
def add_student():
    # name = request.form['name']
    # age = request.form['age']
    # grade = request.form['grade']
    

    # connection = sqlite3.connect('instance/students.db')
    # cursor = connection.cursor()

    # # RAW Query
    # # db.session.execute(
    # #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    # #     {'name': name, 'age': age, 'grade': grade}
    # # )
    # # db.session.commit()
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    # connection.commit()
    # connection.close()
    # return redirect(url_for('index'))

    # Kode baru untuk nomer B.4
    name = request.form.get('name', '').strip()
    age = request.form.get('age', '').strip()
    grade = request.form.get('grade', '').strip()

    # Validasi input
    is_valid, message = validate_input(name, age, grade)
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('index'))  # Redirect jika input tidak valid

    try:
        # Menambahkan data ke database menggunakan SQLAlchemy
        new_student = Student(name=name, age=int(age), grade=grade)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))  # Redirect jika berhasil
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding student: {str(e)}', 'error')
        return redirect(url_for('index'))  # Redirect jika ada erro

@app.route('/delete/<string:id>') 
def delete_student(id):
    # RAW Query
    # db.session.execute(text(f"DELETE FROM student WHERE id={id}")) # Kode awal
    # Penambahan kode baru untuk nomer B.3
    db.session.execute(
        text("DELETE FROM student WHERE id=:id"),
        {'id': id}
    )
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)
    
# Penambahan kode untuk nomer B.1
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == "admin" and password == "password":
            session['user_id'] = 1  
            return redirect(url_for('index'))
        else:
            return "Login gagal, periksa username dan password Anda.", 401
    return render_template('login.html')

# Penambahan kode untuk nomer B.1
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


#Penambahan kode untuk nomer B.4
def validate_input(name, age, grade): 
    if not name or not re.match(r"^[a-zA-Z0-9 ]{2,100}$", name): 
        return False, "Invalid name format. Use only letters, numbers, and spaces (2-100 characters)." 

    try: 
        age_int = int(age) 
        if age_int < 5 or age_int > 100: 
            return False, "Age must be between 5 and 100" 
    except ValueError: 
        return False, "Age must be a valid number" 

    if not grade or not re.match(r"^[a-zA-Z0-9]{1,10}$", grade): 
        return False, "Invalid grade format. Use only letters and numbers (max 10 characters)." 
    return True, "" 


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)
