async def test_health(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_check_db(async_client):
    response = await async_client.get("/health/check-db")
    assert response.status_code == 200
    assert "PostgreSQL 17.7 on x86_64-windows" in response.text


async def test_metrics(async_client):
    response = await async_client.get("/health/metrics")
    assert response.status_code == 200
