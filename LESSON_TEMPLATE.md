# Lesson File Pattern (Use for all future lessons)

Use this structure for every `starter.py`:

1. **Boilerplate at top**
   - imports
   - fixed constants / fill-in values
2. **Full working helper functions**
   - setup
   - action functions
   - utility functions
3. **`main()` with student zone only**
   - student fills a few function calls in sequence
   - all error handling stays inside `main()`
4. **safe cleanup in `finally`**

## Student zone rules
- Keep student edits limited to 3-6 TODO lines.
- Prefer replacing placeholders with:
  - existing variable names
  - function calls
  - small constant values
- Avoid requiring students to write new functions.

## Error handling rules
Always include:
- `except ValueError` for input mistakes
- `except RuntimeError` for hardware/runtime issues
- `except KeyboardInterrupt` for manual stop
- generic `except Exception` fallback
- `finally` cleanup

## Difficulty control
- Phase 1 lessons: only call existing functions.
- Phase 2 lessons: call functions + simple conditions.
- Phase 3 lessons: map model labels to function calls.
- Phase 4 lessons: map language intent to function calls.
