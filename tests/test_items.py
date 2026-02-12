import pytest

@pytest.mark.asyncio
async def test_items_requires_auth(client):
    response = await client.get("/items")
    assert response.status_code == 403
