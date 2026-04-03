# ARCHITECT-BRIEF.md

## Step 1 — 성적 관리 시스템 전면 재설계

### 작업 범위
`/home/blackpc/app.py` 전체 재작성 + `templates/` 전체 교체/신규 + `requirements.txt` 수정

---

### DB 스키마 (3개 테이블)

#### Course (과목)
```python
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)       # 과목명
    year = db.Column(db.Integer, nullable=False)            # 연도
    semester = db.Column(db.String(20), nullable=False)     # 학기 (1학기/2학기/여름/겨울)
    report_weight = db.Column(db.Float, default=20.0)       # 레포트 가중치 %
    attendance_weight = db.Column(db.Float, default=10.0)   # 출석 가중치 %
    midterm_weight = db.Column(db.Float, default=35.0)      # 중간시험 가중치 %
    final_weight = db.Column(db.Float, default=35.0)        # 기말시험 가중치 %
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    students = db.relationship('Student', backref='course', lazy=True, cascade='all, delete-orphan')
    grade_policy = db.relationship('GradePolicy', backref='course', uselist=False, cascade='all, delete-orphan')
```
- Flag: report+attendance+midterm+final weight 합계 = 100 검증 필수

#### GradePolicy (학점 구간 정책)
```python
class GradePolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    a_plus = db.Column(db.Float, default=10.0)   # A+ 상위 %
    a     = db.Column(db.Float, default=15.0)    # A
    b_plus = db.Column(db.Float, default=15.0)   # B+
    b     = db.Column(db.Float, default=20.0)    # B
    c_plus = db.Column(db.Float, default=15.0)   # C+
    c     = db.Column(db.Float, default=10.0)    # C
    d_plus = db.Column(db.Float, default=5.0)    # D+
    d     = db.Column(db.Float, default=5.0)     # D
    # F: 나머지 자동 (100 - 합계)
```
- Flag: a_plus+a+b_plus+b+c_plus+c+d_plus+d <= 100 검증 필수

#### Student (학생)
```python
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    report_score = db.Column(db.Float, nullable=False)      # 레포트 점수
    attendance_score = db.Column(db.Float, nullable=False)  # 출석 점수
    midterm_score = db.Column(db.Float, nullable=False)     # 중간시험 점수
    final_score = db.Column(db.Float, nullable=False)       # 기말시험 점수
    total_score = db.Column(db.Float)                       # 가중 합산 점수 (자동계산)
    grade = db.Column(db.String(2))                         # 학점 (자동배정)
    rank = db.Column(db.Integer)                            # 순위 (자동배정)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 핵심 함수

#### 1. 가중 점수 계산
```python
def calc_total_score(student, course):
    return (
        student.report_score * course.report_weight +
        student.attendance_score * course.attendance_weight +
        student.midterm_score * course.midterm_weight +
        student.final_score * course.final_weight
    ) / 100
```

#### 2. 학점 일괄 재배정 (학생 추가/수정/삭제 후 반드시 호출)
```python
def recalculate_grades(course_id):
    course = Course.query.get(course_id)
    policy = course.grade_policy
    # 정렬: 총점 → 중간시험 → 기말시험 → 레포트 → 출석 (모두 내림차순)
    students = Student.query.filter_by(course_id=course_id).order_by(
        Student.total_score.desc(),
        Student.midterm_score.desc(),
        Student.final_score.desc(),
        Student.report_score.desc(),
        Student.attendance_score.desc()
    ).all()
    n = len(students)
    if n == 0:
        return

    # 각 등급 인원수 계산 (소수점 올림)
    import math
    counts = [
        math.ceil(n * policy.a_plus / 100),
        math.ceil(n * policy.a / 100),
        math.ceil(n * policy.b_plus / 100),
        math.ceil(n * policy.b / 100),
        math.ceil(n * policy.c_plus / 100),
        math.ceil(n * policy.c / 100),
        math.ceil(n * policy.d_plus / 100),
        math.ceil(n * policy.d / 100),
    ]
    grade_labels = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D']

    # 동점자 처리: 같은 점수는 같은 등급
    idx = 0
    for rank, student in enumerate(students, 1):
        student.rank = rank
        # 현재 idx가 가리키는 등급 구간 누적 인원 확인
        cumulative = sum(counts[:idx+1])
        while idx < len(counts) - 1 and rank > cumulative:
            idx += 1
            cumulative = sum(counts[:idx+1])
        if idx < len(grade_labels):
            student.grade = grade_labels[idx]
        else:
            student.grade = 'F'

    db.session.commit()
```
- Flag: 동점자 우선순위 — 중간시험 → 기말시험 → 레포트 → 출석 순으로 정렬 (총점 동점 시 적용)
- Flag: 동점자가 등급 경계에 걸리면 더 높은 등급 부여 (ceil 사용 이유)

---

### 라우트 목록

| Method | URL | 기능 |
|--------|-----|------|
| GET | `/` | 과목 목록 |
| GET/POST | `/course/new` | 과목 생성 (가중치 + 학점정책 동시 설정) |
| GET | `/course/<id>` | 과목 학생 목록 + 순위 |
| GET/POST | `/course/<id>/edit` | 과목명/가중치/학점정책 수정 → recalculate_grades 호출 |
| POST | `/course/<id>/delete` | 과목 삭제 (학생 포함 cascade) |
| GET/POST | `/course/<id>/add_student` | 학생 추가 (4개 점수) |
| GET/POST | `/student/<id>/edit` | 학생 점수 수정 → recalculate_grades 호출 |
| POST | `/student/<id>/delete` | 학생 삭제 → recalculate_grades 호출 |
| GET/POST | `/course/<id>/bulk_add` | 일괄 추가 (이름,레포트,출석,중간,기말 CSV) |
| GET/POST | `/course/<id>/import_excel` | Excel 임포트 |
| GET | `/course/<id>/statistics` | 통계 (과목별) |

---

### 라우트 삭제 대상 (기존 코드)
기존 `add_student`, `bulk_add`, `delete_student`, `clear_all`, `statistics` 라우트 전부 교체.

---

### 템플릿 목록 (신규/교체)

| 파일 | 내용 |
|------|------|
| `base.html` | 네비: 홈(과목목록) 만 표시. 과목별 링크는 동적 |
| `index.html` | 과목 카드 목록. "새 과목 만들기" 버튼 |
| `course_new.html` | 과목명/연도/학기 + 가중치 4개 + 학점구간 8개 입력폼 |
| `course_detail.html` | 학생 테이블 (순위/이름/4점수/총점/학점). 학생추가/Excel가져오기/수정/삭제 버튼 |
| `course_edit.html` | course_new와 동일 구조, 기존값 채워진 수정폼 |
| `add_student.html` | 학생 이름 + 4개 점수 입력 (0~100) |
| `edit_student.html` | add_student와 동일, 기존값 채워짐 |
| `bulk_add.html` | CSV 형식: 이름,레포트,출석,중간,기말 (1행=헤더 스킵) |
| `import_excel.html` | .xlsx 업로드. A=이름 B=레포트 C=출석 D=중간 E=기말 |
| `statistics.html` | 과목별: 평균/최고/최저/등급분포 차트 |

---

### requirements.txt 추가
```
openpyxl
```

---

### Flag 목록
- `recalculate_grades()` 는 학생 추가/수정/삭제/과목설정변경 후 반드시 호출
- 가중치 합계 검증: `report+attendance+midterm+final != 100` 이면 저장 거부
- 학점정책 합계: a_plus+a+b_plus+b+c_plus+c+d_plus+d > 100 이면 저장 거부
- 학생 0명인 과목은 recalculate_grades에서 early return
- Excel/bulk_add 에서 점수 범위 검사: 각 항목 0~100
- 기존 `grade_management.db` 와 스키마 호환 안 됨 — 앱 시작 시 `db.create_all()` 로 새 스키마 생성. 기존 DB 파일 삭제 후 재시작 안내 문구 추가 불필요 (Bob이 판단)
- Bootstrap 5 + Bootstrap Icons 유지
