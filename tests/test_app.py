import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def login(c, user="admin", pw="admin123"):
    return c.post("/login", data={"username": user, "password": pw}, follow_redirects=True)


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_login_page_loads(client):
    assert client.get("/login").status_code == 200


def test_login_success_and_failure(client):
    assert b"Invalid" in login(client, pw="wrong").data
    assert b"Add Employee" in login(client).data


def test_protected_routes_require_login(client):
    assert client.get("/employees").status_code == 302
    assert client.get("/api/employees").status_code == 401


def test_api_crud_cycle(client):
    login(client)
    payload = {"name": "Asha", "email": "asha@x.com", "department": "IT", "salary": 50000}
    r = client.post("/api/employees", json=payload)
    assert r.status_code == 201
    eid = r.get_json()["id"]
    assert client.get(f"/api/employees/{eid}").get_json()["name"] == "Asha"
    payload["department"] = "HR"
    assert client.put(f"/api/employees/{eid}", json=payload).get_json()["department"] == "HR"
    assert len(client.get("/api/employees").get_json()) == 1
    assert client.delete(f"/api/employees/{eid}").status_code == 204
    assert client.get(f"/api/employees/{eid}").status_code == 404


def test_validation_and_duplicates(client):
    login(client)
    assert client.post("/api/employees", json={"name": "x"}).status_code == 400
    ok = {"name": "A", "email": "a@x.com", "department": "IT", "salary": 1}
    client.post("/api/employees", json=ok)
    assert client.post("/api/employees", json=ok).status_code == 409


def test_404_handlers(client):
    assert client.get("/nope").status_code == 404
    login(client)
    assert client.get("/api/employees/999").get_json()["error"]


def test_ui_add_employee(client):
    login(client)
    r = client.post("/employees/add", data={"name": "Ravi", "email": "r@x.com",
                    "department": "Ops", "salary": "100"}, follow_redirects=True)
    assert b"Ravi" in r.data
