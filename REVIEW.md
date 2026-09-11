# Code Review

## 1. SQL Injection in task search - Critical / Security

**File:** `backend/projects/views.py`, `TaskListCreateView.get`

**Status:** Fixed in commit `c942be9`.

Before the fix, the `q` search parameter was interpolated directly into a raw
SQL f-string. A quote character could break the intended SQL string literal
and reach Postgres as executable query text.

**Fix:** Replaced the raw SQL branch with Django ORM `Q` filtering:

```python
Q(title__icontains=q) | Q(description__icontains=q)
```

Django parameterizes the search value automatically.

**Proof before:** [docs/sqli-proof-before.txt](docs/sqli-proof-before.txt)

```text
ProgrammingError: operator is not unique: unknown % unknown
```

**Proof after:** The quote-character regression test returns HTTP 200 with an
empty task list:

```text
HTTP 200, {"tasks": []}
```

## 2. Broken access control on task PATCH - Critical / Security

**File:** `backend/projects/views.py`, `TaskDetailView.patch`

**Status:** Open. No fix is present in the current checkout.

`TaskDetailView.patch` loads a task by ID and updates it without checking
whether the authenticated user belongs to the task's project. Any
authenticated user can therefore edit the title, description, status, or
assignee of a task in a project where they have no membership.

**Proof before:** [docs/access-control-proof-before.txt](docs/access-control-proof-before.txt)

```text
HTTP/1.1 200 OK
{"task": {"title": "hijacked by a non-member", ...}}
```

The same authorization gap remains in the current `TaskDetailView.patch`.
The endpoint should perform the membership and role check used by the other
task mutations before applying changes.

## 3. N+1 query on project list - Medium / Performance

**File:** `backend/projects/views.py`, `ProjectListCreateView.get`

**Status:** Open. No fix is present in the current checkout.

The queryset calls `prefetch_related('project__tasks')`, but the per-project
loop uses `p.tasks.count()`. That issues a fresh `COUNT` query for each
project instead of reusing the prefetched task collection.

**Fix:** Use `len(p.tasks.all())` to reuse the prefetched data, or annotate the
queryset with `Count('project__tasks')` and read the annotation in the loop.

## 4. Non-atomic position assignment - Medium / Data Integrity

**File:** `backend/projects/views.py`, `TaskListCreateView.post`

**Status:** Open. No fix is present in the current checkout.

The code reads the current maximum position and then writes `max + 1` in
separate, unguarded operations. Two concurrent task creates in the same
project and status can read the same maximum and receive the same position.

**Fix:** Wrap the lookup and create in `transaction.atomic()` and lock the
relevant rows with `select_for_update()`. A database-level uniqueness strategy
may also be appropriate if duplicate positions must be impossible.
