# BUILD-LOG — Step 2: 과목별 학생 명단 업로드 + 명단 기반 학생 추가

**Date**: 2026-04-03
**Builder**: Bob
**Status**: Review fixes applied — resubmitted for review

---

## Files Changed

| File | Action | Notes |
|------|--------|-------|
| `/home/blackpc/requirements.txt` | Modified | Added `xlrd` |
| `/home/blackpc/app.py` | Modified | Added `CourseRoster` model, `student_number`/`department` on `Student`, `parse_roster_file()`, 3 new routes, updated `add_student` / `edit_student` |
| `/home/blackpc/templates/course_detail.html` | Modified | Added "명단 업로드" and "명단에서 추가" buttons; roster count badge |
| `/home/blackpc/templates/add_student.html` | Modified | Added optional 학번 / 계열 fields |
| `/home/blackpc/templates/edit_student.html` | Modified | Added optional 학번 / 계열 fields |
| `/home/blackpc/templates/upload_roster.html` | Created | File upload form with 추가/전체교체 radio; shows current roster count + initialise button |
| `/home/blackpc/templates/add_from_roster.html` | Created | Roster table with client-side JS filter; score entry form when row selected |

---

## Key Decisions

1. **xlrd imported at top-level**: `import xlrd` is at the top of `app.py` (not lazily inside the helper). `openpyxl` remains a lazy import inside `parse_roster_file` to match the pattern already used in `import_excel`.

2. **`parse_roster_file` as module-level function**: Not a route helper or class method — keeps it testable and reusable. Raises `ValueError` for all user-facing error cases so the caller can flash the message without ever seeing a raw traceback.

3. **xlrd numeric cell handling**: `xlrd` returns student numbers (e.g. `20231234`) as Python `float` values. The `_cell()` inner function converts `float` → `int` → `str` when the float has no fractional part, preserving leading-zero-free strings (student IDs are not padded in Korean systems).

4. **`student_number` and `department` are nullable on Student**: Existing Step 1 student records have `NULL` for both — downstream templates handle `student.student_number or ''` correctly.

5. **DB migration comment instead of Alembic**: As instructed, a plain comment near `db.create_all()` tells the operator to delete the old DB when upgrading from Step 1.

6. **`add_from_roster` POST redirects on error**: On validation failure the handler redirects back to the same `?roster_id=X` URL rather than re-rendering, so the roster table stays visible and the score form re-opens for the same entry.

7. **`clear_roster` accessible from `upload_roster.html`**: If the course already has a roster, the upload page shows an inline "명단 초기화" button (POST to `/course/<id>/clear_roster`) — no extra page needed.

---

## Review Fixes Applied (2026-04-03)

### Must Fix

1. **requirements.txt — xlrd unpinned** — Changed `xlrd` to `xlrd>=1.2.0,<2` to prevent pip from resolving to xlrd 2.x, which dropped `.xls` support entirely.

### Should Fix

2. **app.py:260 — float inf/nan crash in xlrd cell normalisation** — Added `math.isfinite(val)` guard inside `_cell()`. `inf`/`nan` values from corrupt or formula-error cells now return `''` instead of raising `OverflowError`/`ValueError`. (`import math` was already present at the top of the file.)

3. **app.py:751 — Bulk DELETE bypasses ORM cascade** — Added `synchronize_session='fetch'` to `CourseRoster.query.filter_by(course_id=course_id).delete(...)`. The session identity map is now updated correctly and the pattern is safe if a child table is added later.

4. **templates/upload_roster.html:59–65 — nested form bug** — Moved the "명단 초기화" `<form>` outside the upload `<form>` element. The clear-roster form is now placed after the closing `</form>` of the upload form, visually in the same card body area, resolving the invalid-HTML nesting that caused the inner submit button to trigger the outer form.

---

## Known Gaps / Out of Scope

- No duplicate-detection when appending a roster (same student name/number already in table) — not specified in the brief.
- No "명단에서 추가" button on the empty-course state at the bottom of `course_detail.html` (the button in the header area is already hidden when roster is empty; this matches the brief's conditional).

---

# BUILD-LOG — Step 1: Grade Management System Redesign

**Date**: 2026-04-03
**Builder**: Bob
**Status**: Review fixes applied — resubmitted for review

---

## Files Changed

| File | Action | Notes |
|------|--------|-------|
| `/home/blackpc/requirements.txt` | Modified | Added `openpyxl` |
| `/home/blackpc/app.py` | Full rewrite | 3-model schema, new routes, helpers |
| `/home/blackpc/templates/base.html` | Rewrite | Navbar simplified to Home (과목목록) only |
| `/home/blackpc/templates/index.html` | Rewrite | Course card list |
| `/home/blackpc/templates/course_new.html` | Created | New course form with live weight/policy totals |
| `/home/blackpc/templates/course_detail.html` | Created | Student table with ranks and 4 scores |
| `/home/blackpc/templates/course_edit.html` | Created | Edit form, pre-populated with current values |
| `/home/blackpc/templates/add_student.html` | Rewrite | 4-score form, scoped to a course |
| `/home/blackpc/templates/edit_student.html` | Created | Edit student scores, shows current totals |
| `/home/blackpc/templates/bulk_add.html` | Rewrite | New 5-column CSV format with live preview |
| `/home/blackpc/templates/import_excel.html` | Created | .xlsx upload form |
| `/home/blackpc/templates/statistics.html` | Rewrite | Per-course stats, grade distribution bars, top-10 |
| `/home/blackpc/instance/grade_management.db` | Deleted | Old 1-table schema incompatible with new 3-table schema |

---

## Key Decisions

1. **Old DB deleted**: The old `grade_management.db` schema (single Student table, no Course) is incompatible with the new schema. Flask's `db.create_all()` will create the new schema fresh on next startup.

2. **`recalculate_grades` placement**: Called after every add, edit, delete student operation, and after course settings are saved — exactly as the brief specifies.

3. **Weight/policy validation helpers**: Extracted to `_validate_weights()` and `_validate_policy()` with 0.01 float tolerance so that e.g. `33.33 + 33.33 + 33.34 = 100.00` passes.

4. **`_parse_course_form()` helper**: Centralised form parsing/validation for course creation and editing — prevents duplication between `course_new` and `course_edit` routes.

5. **Bulk add header skip**: Lines starting with `이름` or `name` (case-insensitive) on the first line are treated as header and skipped — mirrors the example in the brief.

6. **Excel import**: `openpyxl` reads the active worksheet from row 2 onward (row 1 = header). Entirely-blank rows are skipped.

7. **Grade label bounds**: After iterating through all grade buckets, any student whose rank exceeds the cumulative total of all non-F buckets receives grade 'F'. This is correct per the brief ("F: 나머지 자동").

8. **`recalculate_grades` total_score update**: `calc_total_score()` is called on every student inside `recalculate_grades`, ensuring `total_score` is always consistent with the current course weights before sorting.

---

## Review Fixes Applied (2026-04-03)

### Must Fix

1. **F grade never assigned (line 139)** — Added `named_total = sum(counts)` before the loop. Each student whose `rank > named_total` is now explicitly assigned `'F'`, bypassing the `grade_labels` lookup entirely. The unreachable `else 'F'` branch has been replaced.

2. **CSV header-skip operator precedence (line 474)** — Added parentheses: `if i == 1 and (line.lower().startswith('이름') or line.lower().startswith('name'))`. The unguarded second OR clause that caused any line starting with "name" to be silently dropped is fixed.

3. **Raw openpyxl exception leaked to user (line 551)** — Changed `except Exception as e` to `except Exception`. Replaced `flash(f'... {e}', 'error')` with a fixed user-facing message. Added `app.logger.exception('Excel parse error')` for server-side logging.

### Should Fix

4. **SECRET_KEY hardcoded (line 13)** — Replaced the literal string with `os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')`. `import os` was already present.

5. **`Course.query.get()` deprecated (line 95)** — Replaced `Course.query.get(course_id)` inside `recalculate_grades` with `db.session.get(Course, course_id)`.

6. **Double commit on course edit (line 336)** — Replaced `db.session.commit()` before `recalculate_grades(course.id)` with `db.session.flush()`. The single commit inside `recalculate_grades` now handles the full write.

---

## Known Gaps / Out of Scope

- No Excel *export* — not in the brief.
- No pagination on the student table — not specified. Can be added later.
- No per-student tiebreaker equality handling (students with identical score on all 5 dimensions share the same bucket via `ceil`; they may still get different sequential ranks because SQLAlchemy's ORDER BY gives them a deterministic but arbitrary secondary order). This is consistent with the brief's ceil-based policy.

---

## Smoke Test

Ran in-memory SQLite test with 5 students. Output:

```
Rank | Name  | Total  | Grade
  1  | Eve   | 97.25  | A+
  2  | Alice | 90.50  | A
  3  | Carol | 83.45  | B+
  4  | Bob   | 76.80  | B
  5  | Dave  | 58.05  | C+
```

Grade assignment and tiebreaker sorting confirmed correct.
