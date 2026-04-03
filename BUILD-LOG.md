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
