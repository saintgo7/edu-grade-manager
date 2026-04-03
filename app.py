from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grade_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Student {self.name}>'

def get_grade(score):
    """점수에 따른 등급 계산"""
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 85:
        return "B+"
    elif score >= 80:
        return "B"
    elif score >= 75:
        return "C+"
    elif score >= 70:
        return "C"
    elif score >= 65:
        return "D+"
    elif score >= 60:
        return "D"
    else:
        return "F"

@app.route('/')
def index():
    """메인 페이지 - 모든 학생 목록 표시"""
    students = Student.query.order_by(Student.created_at.desc()).all()
    
    # 성적 분포 계산
    grade_distribution = {}
    if students:
        for student in students:
            grade = student.grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    return render_template('index.html', students=students, grade_distribution=grade_distribution)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """학생 추가 페이지"""
    if request.method == 'POST':
        name = request.form['name'].strip()
        try:
            score = float(request.form['score'])
        except ValueError:
            flash('점수는 숫자로 입력해주세요.', 'error')
            return render_template('add_student.html')
        
        # 유효성 검사
        if not name:
            flash('학생 이름을 입력해주세요.', 'error')
            return render_template('add_student.html')
        
        if not (0 <= score <= 100):
            flash('점수는 0~100 사이의 값이어야 합니다.', 'error')
            return render_template('add_student.html')
        
        # 등급 계산
        grade = get_grade(score)
        
        # 데이터베이스에 저장
        student = Student(name=name, score=score, grade=grade)
        db.session.add(student)
        db.session.commit()
        
        flash(f'{name} 학생이 성공적으로 추가되었습니다. (점수: {score}, 등급: {grade})', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_student.html')

@app.route('/bulk_add', methods=['GET', 'POST'])
def bulk_add():
    """여러 학생 일괄 추가 페이지"""
    if request.method == 'POST':
        students_data = request.form['students_data'].strip()
        
        if not students_data:
            flash('학생 데이터를 입력해주세요.', 'error')
            return render_template('bulk_add.html')
        
        lines = students_data.split('\n')
        added_count = 0
        errors = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                parts = line.split(',')
                if len(parts) != 2:
                    errors.append(f'라인 {i}: 형식이 올바르지 않습니다. (이름,점수 형식으로 입력해주세요)')
                    continue
                
                name = parts[0].strip()
                score = float(parts[1].strip())
                
                if not name:
                    errors.append(f'라인 {i}: 학생 이름이 비어있습니다.')
                    continue
                
                if not (0 <= score <= 100):
                    errors.append(f'라인 {i}: 점수는 0~100 사이여야 합니다.')
                    continue
                
                grade = get_grade(score)
                student = Student(name=name, score=score, grade=grade)
                db.session.add(student)
                added_count += 1
                
            except ValueError:
                errors.append(f'라인 {i}: 점수는 숫자여야 합니다.')
            except Exception as e:
                errors.append(f'라인 {i}: 오류 발생 - {str(e)}')
        
        if added_count > 0:
            db.session.commit()
            flash(f'{added_count}명의 학생이 성공적으로 추가되었습니다.', 'success')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        
        return redirect(url_for('index'))
    
    return render_template('bulk_add.html')

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    """학생 삭제"""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'{student.name} 학생이 삭제되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/clear_all')
def clear_all():
    """모든 학생 데이터 삭제"""
    Student.query.delete()
    db.session.commit()
    flash('모든 학생 데이터가 삭제되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/statistics')
def statistics():
    """통계 페이지"""
    students = Student.query.all()
    
    if not students:
        return render_template('statistics.html', students=[], stats={})
    
    # 기본 통계 계산
    scores = [s.score for s in students]
    total_students = len(students)
    average_score = sum(scores) / total_students
    highest_score = max(scores)
    lowest_score = min(scores)
    
    # 성적 분포
    grade_distribution = {}
    for student in students:
        grade = student.grade
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    # 등급별 백분율
    grade_percentages = {}
    for grade, count in grade_distribution.items():
        grade_percentages[grade] = round((count / total_students) * 100, 1)
    
    stats = {
        'total_students': total_students,
        'average_score': round(average_score, 2),
        'highest_score': highest_score,
        'lowest_score': lowest_score,
        'grade_distribution': grade_distribution,
        'grade_percentages': grade_percentages
    }
    
    return render_template('statistics.html', students=students, stats=stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)