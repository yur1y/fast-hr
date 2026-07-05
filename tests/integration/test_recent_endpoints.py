from fastapi.testclient import TestClient

from app.main import app


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


class DummyJobRepo:
    def __init__(self, session=None):
        self.session = session

    async def list_all(self, limit=100, offset=0):
        return []

    async def list_active(self, limit=50, offset=0):
        return []

    async def get_by_id(self, job_id):
        return None


class DummyApplicationRepo:
    def __init__(self, session=None):
        self.session = session

    async def list_all(self, limit=100, offset=0):
        return []

    async def get_by_id(self, application_id):
        return None


def test_admin_jobs_and_candidates_pages_render(monkeypatch):
    client = TestClient(app)
    jobs_resp = client.get("/admin/jobs")
    candidates_resp = client.get("/admin/candidates")

    assert jobs_resp.status_code == 200
    assert candidates_resp.status_code == 200
    assert "<!doctype html>" in jobs_resp.text.lower()
    assert "tracepilot" in jobs_resp.text.lower()
    assert "<!doctype html>" in candidates_resp.text.lower()


def test_careers_jobs_page_renders(monkeypatch):
    async def fake_get_db():
        yield DummyDB()

    monkeypatch.setattr("app.api.v1.endpoints.careers.get_db", fake_get_db)
    monkeypatch.setattr("app.api.v1.endpoints.careers.JobRepository", DummyJobRepo)

    client = TestClient(app)
    resp = client.get("/api/v1/careers/jobs")

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


def test_admin_screenings_page_renders(monkeypatch):
    client = TestClient(app)
    resp = client.get("/admin/screenings")

    assert resp.status_code == 200
    assert "<!doctype html>" in resp.text.lower()
    assert "tracepilot" in resp.text.lower()


def test_screenings_api_limit_param(monkeypatch):
    async def fake_get_db():
        yield DummyDB()

    class FakeRepo:
        async def list_recent(self, limit=100):
            return []

        async def list_all(self):
            return []

        def to_dict(self, obj):
            return {}

    from app.api.deps import get_db

    monkeypatch.setattr(
        "app.api.v1.endpoints.screenings.ScreeningRepository",
        lambda db: FakeRepo(),
    )
    app.dependency_overrides[get_db] = fake_get_db
    try:
        client = TestClient(app)
        resp = client.get("/api/v1/screenings?limit=50")

        assert resp.status_code == 200
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

    async def fake_get_db():
        yield DummyDB()

    from app.api.deps import get_db

    monkeypatch.setattr("app.api.v1.endpoints.careers.JobRepository", FakeJobRepo)
    app.dependency_overrides[get_db] = fake_get_db
    try:
        client = TestClient(app)
        resp = client.get("/api/v1/careers/jobs")
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_admin_list_jobs(monkeypatch):
    class FakeJobRepo:
        def __init__(self, session=None):
            self.session = session

        async def list_all(self, limit=100, offset=0):
            return []

        async def get_by_id(self, job_id):
            return None

    async def fake_get_db():
        yield DummyDB()

    from app.api.deps import get_db

    monkeypatch.setattr("app.api.v1.endpoints.admin.JobRepository", FakeJobRepo)
    app.dependency_overrides[get_db] = fake_get_db
    try:
        client = TestClient(app)
        resp = client.get("/api/v1/admin/jobs")
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db, None)


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

    async def fake_get_db():
        yield DummyDB()

    from app.api.deps import get_db

    monkeypatch.setattr("app.api.v1.endpoints.admin.ApplicationRepository", FakeAppRepo)
    monkeypatch.setattr("app.api.v1.endpoints.admin.JobRepository", FakeJobRepo)
    app.dependency_overrides[get_db] = fake_get_db
    try:
        client = TestClient(app)
        resp = client.get("/api/v1/admin/candidates")
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db, None)
