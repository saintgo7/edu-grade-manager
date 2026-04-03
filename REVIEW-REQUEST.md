# REVIEW-REQUEST — Step 2: 과목별 학생 명단 업로드 + 명단 기반 학생 추가

**Date**: 2026-04-03
**Builder**: Bob
**Ready for Review**: YES

---

## Review Fixes Applied (from REVIEW-FEEDBACK.md, 2026-04-03)

| # | Location | Fix |
|---|----------|-----|
| 1 (Must) | `requirements.txt:4` | Pinned `xlrd` to `xlrd>=1.2.0,<2` — prevents xlrd 2.x install which dropped `.xls` support |
| 2 (Should) | `app.py:260` | Added `math.isfinite(val)` guard in `_cell()` — corrupt/formula-error cells returning `inf`/`nan` now produce `''` instead of raising `OverflowError`/`ValueError` |
| 3 (Should) | `app.py:751` | Added `synchronize_session='fetch'` to bulk DELETE in 전체교체 mode — keeps ORM session consistent with cascade declaration |
| 4 (Should) | `templates/upload_roster.html:59–65` | Moved "명단 초기화" `<form>` outside the upload `<form>` — fixes invalid nested-form HTML that caused the inner submit to trigger the outer form |

---

## Changed Files

### `/home/blackpc/requirements.txt` (line 4)
Changed `xlrd` to `xlrd>=1.2.0,<2` to support parsing of legacy `.xls` Excel files without resolving to the incompatible xlrd 2.x.

---

### `/home/blackpc/app.py`

| Lines | Change |
|-------|--------|
| 7 | Added `import xlrd` at module level. |
| 68–69 | Added `student_number` (String 50, nullable) and `department` (String 100, nullable) columns to the `Student` model. |
| 83–96 | New `CourseRoster` model with `course_id` FK, `department`, `name`, `student_number`; back-populated onto `Course.roster` with cascade delete. |
| 195–273 | New `parse_roster_file(file_data, filename)` helper — routes `.xlsx` to openpyxl and `.xls` to xlrd, detects columns by header name, normalises xlrd float student-IDs to int strings, raises `ValueError` with user-facing messages on all error paths. |
| 486–495 | Updated `add_student` POST handler to read `student_number` and `department` from the form and pass them to the `Student` constructor. |
| 532–534 | Updated `edit_student` POST handler to update `student.student_number` and `student.department` from the form. |
| 726–766 | New `upload_roster` route (GET/POST) — reads the uploaded file via `parse_roster_file`, respects "추가"/"전체교체" mode radio, commits `CourseRoster` rows, flashes count, redirects to course detail. |
| 769–776 | New `clear_roster` route (POST) — deletes all `CourseRoster` rows for the course. |
| 779–853 | New `add_from_roster` route (GET/POST) — GET serves roster table + optional score form when `?roster_id=X` query param is present; POST creates a `Student` and calls `recalculate_grades`. |
| 900–908 | Added upgrade comment near `db.create_all()` instructing operators to delete `grade_management.db` when upgrading from Step 1. |

---

### `/home/blackpc/templates/course_detail.html` (lines 18–42)
Added "명단 업로드" button (always visible, with roster count badge when non-empty) and "명단에서 추가" button (shown only when `course.roster` is non-empty).

---

### `/home/blackpc/templates/add_student.html` (lines 22–38)
Added optional 학번 and 계열 text inputs in a two-column row above the score fields.

---

### `/home/blackpc/templates/edit_student.html` (lines 22–38)
Added optional 학번 and 계열 text inputs pre-populated from `student.student_number` / `student.department`.

---

### `/home/blackpc/templates/upload_roster.html` (new file, 74 lines)
File upload form accepting `.xls`/`.xlsx` with 추가/전체교체 radio; shows current roster count and an inline "명단 초기화" button when roster exists.

---

### `/home/blackpc/templates/add_from_roster.html` (new file, 150 lines)
Roster table (계열, 이름, 학번 columns, "선택" button per row); client-side JS filter (계열 dropdown + 이름/학번 text search via row show/hide, no server request); when `?roster_id=X` is in the URL, a pre-filled score entry form appears above the table.

---

## Open Questions

None — brief was unambiguous.
