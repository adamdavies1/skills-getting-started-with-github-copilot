# Testing Guide

This directory contains comprehensive tests for the Mergington High School Activities API.

## Running Tests

### Run all tests
```bash
pytest tests/test_app.py -v
```

### Run specific test class
```bash
pytest tests/test_app.py::TestGetActivities -v
pytest tests/test_app.py::TestSignupForActivity -v
pytest tests/test_app.py::TestUnregisterFromActivity -v
```

### Run specific test
```bash
pytest tests/test_app.py::TestSignupForActivity::test_signup_success -v
```

### Run with coverage report
```bash
pytest tests/test_app.py --cov=src --cov-report=html
```
This generates an HTML coverage report in `htmlcov/index.html`

### Run with verbose output
```bash
pytest tests/test_app.py -vv
```

### Run with print statements visible
```bash
pytest tests/test_app.py -s
```

---

## Test Structure

### Fixtures (`tests/test_app.py`)

**`fresh_activities`** — Provides isolated test data
- Deep copies the original activities dictionary
- Monkeypatches the app's activities for test isolation
- Ensures no cross-test contamination
- Each test gets a fresh state

**`client`** — Provides TestClient for HTTP requests
- Used to make requests to endpoints
- Simulates HTTP calls without a running server

---

## Test Classes

### `TestGetActivities`
Tests for the GET `/activities` endpoint.

| Test | Purpose |
|------|---------|
| `test_get_activities_returns_all_activities` | Verify endpoint returns all 9 activities |
| `test_get_activities_response_structure` | Verify response has required fields (description, schedule, max_participants, participants) |
| `test_get_activities_participant_data` | Verify participant lists contain correct data |
| `test_root_redirect` | Verify GET / redirects to /static/index.html |

**Coverage**: Happy path + response validation

---

### `TestSignupForActivity`
Tests for the POST `/activities/{activity_name}/signup` endpoint.

| Test | Purpose |
|------|---------|
| `test_signup_success` | Happy path: New participant signs up successfully (200) |
| `test_signup_adds_participant_to_list` | Verify participant is added to activity |
| `test_signup_invalid_email_format` | Email format validation test (API accepts any string) |
| `test_signup_activity_not_found` | Non-existent activity returns 404 |
| `test_signup_duplicate_registration` | Duplicate signup returns 400 |
| `test_signup_different_activities` | Same student can sign up for multiple activities |

**Coverage**: Happy path + 4 error scenarios + edge case (multi-activity signup)

**Error Cases Covered**:
- ❌ Email format (accepts any string, no validation) → 200
- ❌ Resource not found (activity doesn't exist) → 404
- ❌ Conflict (already signed up) → 400

---

### `TestUnregisterFromActivity`
Tests for the DELETE `/activities/{activity_name}/participants/{email}` endpoint.

| Test | Purpose |
|------|---------|
| `test_unregister_success` | Happy path: Participant unregisters successfully (200) |
| `test_unregister_removes_participant` | Verify participant is removed from activity |
| `test_unregister_activity_not_found` | Non-existent activity returns 404 |
| `test_unregister_email_not_registered` | Email not in participants returns 400 |
| `test_unregister_already_unregistered` | Unregistering twice fails on second attempt (400) |

**Coverage**: Happy path + 3 error scenarios

**Error Cases Covered**:
- ❌ Resource not found (activity doesn't exist) → 404
- ❌ Conflict (email not registered) → 400
- ❌ Idempotency (double unregister) → 400

---

## Test Data Isolation

Each test uses the `fresh_activities` fixture which:
1. Creates a deep copy of the original activities data
2. Monkeypatches `src.app.activities` to use this copy
3. Ensures modifications don't affect other tests

This means:
- ✅ Tests can run in any order
- ✅ Tests don't affect each other
- ✅ No need for cleanup or setup/teardown
- ✅ Truly isolated unit tests

---

## Coverage

**Endpoints**: 3/3 (100%)
- ✅ GET /activities
- ✅ POST /activities/{activity_name}/signup
- ✅ DELETE /activities/{activity_name}/participants/{email}

**Test Cases**: 15 total
- ✅ 6 happy path tests
- ✅ 9 error/edge case tests

**Expected Coverage**: ~100% line coverage of `src/app.py` endpoints

### ✅ Actual Coverage: 100%
```
src/app.py: 33 statements, 0 missed = 100% coverage
```

---

## Common Commands

```bash
# Run all tests with summary
pytest tests/test_app.py

# Run with detailed output (shows each assertion)
pytest tests/test_app.py -vv

# Run and stop on first failure
pytest tests/test_app.py -x

# Run and show local variables on failure
pytest tests/test_app.py -l

# Run specific test and show print output
pytest tests/test_app.py::TestSignupForActivity::test_signup_success -s

# Generate coverage report and open in browser
pytest tests/test_app.py --cov=src --cov-report=html && open htmlcov/index.html
```

---

## Debugging

### View detailed test output
```bash
pytest tests/test_app.py -vv
```

### See what's being tested
```bash
pytest tests/test_app.py --collect-only
```

### Debug a specific test
```bash
pytest tests/test_app.py::TestSignupForActivity::test_signup_success -vv --tb=short
```

### Use pdb debugger
Add `import pdb; pdb.set_trace()` in test and run with `-s` flag:
```bash
pytest tests/test_app.py::TestSignupForActivity::test_signup_success -s
```

---

## Future Enhancements

1. **Capacity Testing**: Add tests for max_participants limits
2. **Performance Tests**: Add pytest-benchmark for response times
3. **Database Integration**: When moving to persistent storage, update fixtures to use test database
4. **CI/CD**: Add GitHub Actions workflow to run tests on push/PR
5. **Load Testing**: Add locust for load/stress testing
