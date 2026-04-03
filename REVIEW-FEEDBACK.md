# Review Feedback — Step 2
Date: 2026-04-03
Ready for Builder: NO

---

## Must Fix

- **requirements.txt:4** — `xlrd` is unpinned. xlrd 2.0.0 (released 2020) dropped `.xls` support entirely. `pip install xlrd` on any modern machine resolves to 2.x, which cannot open `.xls` files at all. The xlrd path in `parse_roster_file` will fail on every fresh install. Fix: pin to `xlrd>=1.2.0,<2` in requirements.txt.

---

## Should Fix

- **app.py:260** — The float-to-int conversion `val == int(val)` raises `OverflowError` or `ValueError` for `float('inf')` and `float('nan')`, which xlrd can produce for corrupt or formula-error cells. Add a `math.isfinite(val)` guard: `if isinstance(val, float) and math.isfinite(val) and val == int(val)`.

- **app.py:751** — `CourseRoster.query.filter_by(course_id=course_id).delete()` issues a bulk SQL DELETE that bypasses SQLAlchemy's ORM-level cascade. `CourseRoster` has no child relationships today so there is no functional bug, but the pattern is inconsistent with the cascade declaration on the backref and will silently break if a child table is added later.

- **templates/upload_roster.html:59–65** — The "명단 초기화" `<form>` is nested inside the outer upload `<form method="POST" enctype="multipart/form-data">`. Nested form elements are invalid HTML; browsers silently ignore the inner form and its submit button will submit the outer form instead of POSTing to `clear_roster`. Move the "명단 초기화" form element outside the upload form.

---

## Escalate to Architect

None.

---

## Cleared

- `parse_roster_file()` — `.xlsx` path via `openpyxl`/`io.BytesIO` is correct. `.xls` path via `xlrd.open_workbook(file_contents=...)` is correct in intent (blocked only by the unversioned pin in Must Fix). Column detection is header-name based and position-independent. `ValueError` is raised with user-facing messages for wrong extension, missing name column, and empty file. Header-only files produce an empty list, caught by the route.
- `upload_roster` route — "전체교체" mode deletes only `CourseRoster` rows filtered by `course_id` before inserting. `Student` records are on a separate relationship and are not touched. "추가" mode appends correctly. No raw exception surfaces to users.
- `clear_roster` route — POST-only (`methods=['POST']`). Deletes only `CourseRoster` rows, not `Student` records. No raw exception surfaces to users.
- `add_from_roster` GET — `roster_id` is validated as an integer and cross-checked against `course_id` to prevent cross-course access; falls back gracefully to `None` on bad input. Pre-fills name, student_number, and department from the selected roster entry. Correct.
- `add_from_roster` POST — Creates `Student` with name/student_number/department from form; `recalculate_grades()` called after commit; score validation via `_parse_score` enforces 0–100 range; no raw exception surfaces to users. Correct.
- `Student` model — `student_number` (String 50) and `department` (String 100) are nullable with no `NOT NULL` constraint. No breaking change to existing records. Correct.
- Float student-ID normalisation — `str(int(val))` correctly converts `20230001.0` to `"20230001"` (subject to the `math.isfinite` caveat noted in Should Fix above).
- JS client-side filter — AND logic is correct: `deptOk && queryOk`. Department dropdown does exact-match on `data-dept`. Text search matches `data-name` OR `data-num` (OR within the text criterion is correct behaviour — a user searching by name or by student number). Both filter criteria are combined with AND. Correct.
- Cascade safety — `CourseRoster` cascade `all, delete-orphan` is on the `Course → CourseRoster` backref only. The `Course → Student` relationship is a separate backref. Deleting `CourseRoster` rows does not touch `Student` records.
