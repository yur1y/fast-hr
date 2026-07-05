from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_db


class DummyResult:
    def scalars(self):
        return self

    def unique(self):
        return self

    def all(self):
        return []


class DummyDB:
    async def execute(self, query):
        return DummyResult()


def _with_fake_db(client_call):
    """Run a TestClient call with a fake DB dependency."""
    async def fake_get_db():
        yield DummyDB()

    app.dependency_overrides[get_db] = fake_get_db
    try:
        return client_call()
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_careers_list_jobs(monkeypatch):
    class FakeJobRepo:
        def __init__(self, session=None):
            self.session = session

        async def list_active(self, limit=50, offset=0):
            return []

        async def get_by_id(self, job_id):
            return None

    monkeypatch.setattr("app.api.v1.endpoints.careers.JobRepository", FakeJobRepo)

    client = TestClient(app)
    resp = _with_fake_db(lambda: client.get("/api/v1/careers/jobs"))
    assert resp.status_code == 200


def test_admin_list_jobs(monkeypatch):
    class FakeJobRepo:
        def __init__(self, session=None):
            self.session = session

        async def list_all(self, limit=100, offset=0):
            return []

        async def get_by_id(self, job_id):
            return None

    monkeypatch.setattr("app.api.v1.endpoints.admin.JobRepository", FakeJobRepo)

    client = TestClient(app)
    resp = _with_fake_db(lambda: client.get("/api/v1/admin/jobs"))
    assert resp.status_code == 200


def test_admin_list_candidates(monkeypatch):
    class FakeAppRepo:
        def __init__(self, session=None):
            self.session = session

        async def list_all(self, limit=100, offset=0):
            return []

        async def get_by_id(self, application_id):
            return None

    class FakeJobRepo:
        def __init__(self, session=None):
            self.session = session

        async def get_by_id(self, job_id):
            return None

    monkeypatch.setattr("app.api.v1.endpoints.admin.ApplicationRepository", FakeAppRepo)
    monkeypatch.setattr("app.api.v1.endpoints.admin.JobRepository", FakeJobRepo)

    client = TestClient(app)
    resp = _with_fake_db(lambda: client.get("/api/v1/admin/candidates"))
    assert resp.status_code == 200


def test_screenings_api_limit_param(monkeypatch):
    class FakeRepo:
        async def list_recent(self, limit=100):
            return []

        async def list_all(self):
            return []

        def to_dict(self, obj):
            return {}

    monkeypatch.setattr(
        "app.api.v1.endpoints.screenings.ScreeningRepository",
        lambda db: FakeRepo(),
    )

    client = TestClient(app)
    resp = _with_fake_db(lambda: client.get("/api/v1/screenings?limit=50"))
    assert resp.status_code == 200


def test_task_status_endpoint_uses_expected_path(monkeypatch):
    class DummyAsyncResult:
        status = "SUCCESS"

        def ready(self):
            return True

        @property
        def result(self):
            return {"ok": True}

    monkeypatch.setattr(
        "app.api.v1.endpoints.tasks.celery_app.AsyncResult",
        lambda task_id: DummyAsyncResult(),
    )

    client = TestClient(app)
    resp = client.get("/api/v1/tasks/test-task-id")

    assert resp.status_code == 200
    assert resp.json()["task_id"] == "test-task-id"
    assert resp.json()["status"] == "SUCCESS"
