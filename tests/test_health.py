async def test_health(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_check_db(async_client):
    response = await async_client.get("/health/check-db")
    assert response.status_code == 200


async def test_metrics(async_client):
    response = await async_client.get("/health/metrics")
    assert response.status_code == 200
