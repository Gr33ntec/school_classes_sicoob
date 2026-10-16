import pytest

pytestmark = pytest.mark.integration


def _post(client, path, body, status=201):
    r = client.post(f"/api/v1/{path}", json=body)
    assert r.status_code == status, r.text
    return r.json()


@pytest.fixture
def klass(client):
    course = _post(client, "courses", {"course_code": "C1", "name": "Mat", "workload_hours": 40})
    teacher = _post(client, "teachers", {"employee_code": "T1", "full_name": "Prof"})
    return _post(
        client,
        "classes",
        {
            "class_code": "K1", "course_id": course["id"], "teacher_id": teacher["id"],
            "start_date": "2026-01-01", "end_date": "2026-06-01", "max_students": 1,
        },
    )


def _student(client, code):
    return _post(client, "students", {"registration_code": code, "full_name": f"Aluno {code}"})


def test_crud_and_pagination(client):
    for i in range(3):
        _student(client, f"S{i}")
    r = client.get("/api/v1/students", params={"page": 1, "page_size": 2, "sort": "id", "order": "desc"})
    body = r.json()
    assert r.status_code == 200 and body["total"] == 3 and len(body["items"]) == 2
    sid = body["items"][0]["id"]
    r = client.put(f"/api/v1/students/{sid}", json={"registration_code": "X", "full_name": "Novo"})
    assert r.status_code == 200 and r.json()["full_name"] == "Novo"
    assert client.delete(f"/api/v1/students/{sid}").status_code == 204
    assert client.get(f"/api/v1/students/{sid}").status_code == 404


def test_page_size_limit_and_invalid_sort(client):
    assert client.get("/api/v1/students", params={"page_size": 1000}).status_code == 422
    assert client.get("/api/v1/students", params={"sort": "nope"}).status_code == 422


def test_blank_email_is_not_a_duplicate(client):
    for code in ("A", "B"):
        _post(client, "students", {"registration_code": code, "full_name": "x", "email": ""})


def test_duplicate_code_conflict(client):
    _student(client, "S1")
    _post(client, "students", {"registration_code": "S1", "full_name": "y"}, status=409)


def test_invalid_dates_rejected(client, klass):
    body = {**klass, "class_code": "K2", "start_date": "2026-06-01", "end_date": "2026-01-01"}
    _post(client, "classes", body, status=422)


def test_missing_reference_conflict(client):
    _post(client, "enrollments", {"student_id": 999, "class_id": 999}, status=409)


def test_class_full_and_duplicate_enrollment(client, klass):
    s1, s2 = _student(client, "S1"), _student(client, "S2")
    _post(client, "enrollments", {"student_id": s1["id"], "class_id": klass["id"]})
    _post(client, "enrollments", {"student_id": s1["id"], "class_id": klass["id"]}, status=409)
    r = client.post("/api/v1/enrollments", json={"student_id": s2["id"], "class_id": klass["id"]})
    assert r.status_code == 409 and "lotada" in r.json()["detail"]


def test_cancelled_enrollment_frees_seat(client, klass):
    s1, s2 = _student(client, "S1"), _student(client, "S2")
    e = _post(client, "enrollments", {"student_id": s1["id"], "class_id": klass["id"]})
    client.put(
        f"/api/v1/enrollments/{e['id']}",
        json={"student_id": s1["id"], "class_id": klass["id"], "status": "cancelled"},
    )
    _post(client, "enrollments", {"student_id": s2["id"], "class_id": klass["id"]})


def test_delete_with_relations_conflict(client, klass):
    assert client.delete(f"/api/v1/courses/{klass['course_id']}").status_code == 409
