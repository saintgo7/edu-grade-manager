# Review Feedback — Step 1 (Re-review after fixes)
Date: 2026-04-03
Ready for Builder: YES

---

## Must Fix

None.

---

## Should Fix

None.

---

## Escalate to Architect

None.

---

## Cleared

All six items from the previous review have been verified correct in `/home/blackpc/app.py`.

**Fix 1 — F grade logic (lines 132–143)**
Verified. `named_total = sum(counts)` is computed once before the loop. The `while`
loop advances `idx` through grade buckets using cumulative counts. The condition
`rank > named_total` correctly assigns 'F' to any student whose rank exceeds the total
number of named-grade slots.

Edge case analysis:
- All students pass (policy bands sum to 100%): `math.ceil` rounding may produce
  `named_total >= n`. Since rank maxes at `n`, `rank > named_total` is either never true
  or only triggered when rounding genuinely under-allocates. When bands sum exactly to
  100% and rounding over-allocates, `named_total > n` and no student receives 'F'.
  Correct behaviour.
- Boundary exact match (`rank == named_total`): condition is `rank > named_total`,
  which is `False`. Student receives a letter grade, not 'F'. Correct.
- All students fail (all bands set to 0%): `named_total == 0`, every rank is positive,
  every student gets 'F'. Correct.
- Zero-count intermediate bucket (e.g. A band = 0%): the `while` loop advances `idx`
  past the empty bucket because cumulative does not change, landing on the next
  non-zero label without skipping any student. Correct.

**Fix 2 — CSV header-skip parentheses (line 474)**
Verified. Condition now reads:
`if i == 1 and (line.lower().startswith('이름') or line.lower().startswith('name')):`
The `or` is parenthesised; operator precedence is correct. The `i == 1` guard applies
to both branches. A student named "Namewoo Kim" on row 2+ will no longer be silently
dropped.

**Fix 3 — openpyxl exception handling (lines 551–553)**
Verified. Raw `{e}` is gone. The `except` clause is bare (`except Exception:`),
`app.logger.exception('Excel parse error')` logs the full traceback server-side, and
the user-facing flash message is a fixed, safe Korean string with no exception detail.
Information-disclosure risk eliminated.

**Fix 4 — SECRET_KEY from environment (line 13)**
Verified. `app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')`.
Environment variable is respected in production; fallback is present for local dev only.

**Fix 5 — `db.session.get()` replacement (line 95)**
Verified. The single deprecated `Course.query.get()` call in `recalculate_grades` is
now `db.session.get(Course, course_id)`. A full-file grep confirms zero remaining
`.query.get(` calls. The `.query.get_or_404()` calls at lines 300, 310, 348, 363, 399,
440, 457, 535, and 617 are a distinct Flask-SQLAlchemy convenience method, were not
in scope for this fix, and are not flagged. If a SQLAlchemy 2.x migration is planned,
Arch should log a follow-up task for those call sites.

**Fix 6 — Double commit removed (lines 336–337)**
Verified. The first `db.session.commit()` in `course_edit` is now `db.session.flush()`.
The flush writes updated `course` and `policy` field values into the session transaction,
making them visible to the subsequent `recalculate_grades()` call without committing.
`recalculate_grades()` issues the single `db.session.commit()` at line 145, atomically
committing course/policy updates and all recalculated student grades together.
Single commit path confirmed. No double-write regression.

---

Step 1 is clear.
