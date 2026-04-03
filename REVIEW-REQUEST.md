# REVIEW-REQUEST — Step 1: Grade Management System Redesign

**Ready for Review: YES**
**Date**: 2026-04-03 (fixes applied 2026-04-03)
**Builder**: Bob

---

## Files Submitted for Review

### 1. `/home/blackpc/requirements.txt` (lines 1-3)
Added `openpyxl` as the third dependency alongside the existing Flask and Flask-SQLAlchemy entries.

### 2. `/home/blackpc/app.py` (lines 1-375)
Full rewrite: defines three SQLAlchemy models (Course, GradePolicy, Student), two validation helpers (`_validate_weights`, `_validate_policy`), a shared form-parser (`_parse_course_form`), `calc_total_score`, `recalculate_grades`, and all 11 routes listed in the brief.

### 3. `/home/blackpc/templates/base.html` (lines 1-80)
Navbar trimmed to a single "과목 목록" link pointing to `url_for('index')`; added `{% block scripts %}` slot for per-page JS; added rank-badge CSS helpers used by course_detail.

### 4. `/home/blackpc/templates/index.html` (lines 1-62)
Course card grid showing year/semester, student count, 4 weight badges, and action buttons (학생 목록, 통계, 수정, 삭제 with confirm dialog).

### 5. `/home/blackpc/templates/course_new.html` (lines 1-130)
Three-section form (과목 정보, 가중치, 학점 구간) with live JS totals that flag invalid weight/policy sums in red before submission.

### 6. `/home/blackpc/templates/course_edit.html` (lines 1-138)
Identical form structure to course_new but pre-populated from the `course` and `policy` objects; shows a warning banner that recalculation will occur on save.

### 7. `/home/blackpc/templates/course_detail.html` (lines 1-104)
Student table showing rank (gold/silver/bronze badges for top 3), individual 4-score columns, weighted total, letter grade badge, plus edit/delete per row; header action bar with all bulk entry links.

### 8. `/home/blackpc/templates/add_student.html` (lines 1-57)
4-score form (레포트, 출석, 중간시험, 기말시험) scoped to the current course, with a weight-reminder banner below the inputs.

### 9. `/home/blackpc/templates/edit_student.html` (lines 1-70)
Same 4-score form as add_student, but pre-populated with the student's existing scores; displays current total, grade, and rank as a status reminder.

### 10. `/home/blackpc/templates/bulk_add.html` (lines 1-120)
Updated CSV format from 2-column to 5-column (이름,레포트,출석,중간,기말); live preview table validates each row client-side; course weight display in the help panel.

### 11. `/home/blackpc/templates/import_excel.html` (lines 1-62)
Excel .xlsx upload form with column-layout instructions (A=이름, B-E=scores) and weight reminder; delegates all parsing to the backend.

### 12. `/home/blackpc/templates/statistics.html` (lines 1-133)
Per-course stats page: 4-card summary row (students, avg, high, low), grade distribution progress bars, top-10 ranking table, and A/B-C/D-F group summary cards.

---

## Fixes Applied Since Last Review

All six items from REVIEW-FEEDBACK.md have been addressed:

| # | Severity | Location | Fix |
|---|----------|----------|-----|
| 1 | Must Fix | line 132-143 | F grade now assigned when `rank > named_total`; unreachable else branch removed |
| 2 | Must Fix | line 474 | Parentheses added to CSV header-skip condition to fix operator precedence |
| 3 | Must Fix | line 551-553 | Exception no longer exposed to user; `app.logger.exception` added for server log |
| 4 | Should Fix | line 13 | SECRET_KEY reads from `os.environ.get()` with dev fallback |
| 5 | Should Fix | line 95 | `Course.query.get()` replaced with `db.session.get(Course, ...)` |
| 6 | Should Fix | line 336 | First `db.session.commit()` in course_edit replaced with `db.session.flush()` |

---

## Open Questions for Reviewer

None — the brief was unambiguous on all points. All flags from the brief have been implemented.
