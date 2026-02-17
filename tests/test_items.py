import pytest


@pytest.mark.asyncio
async def test_items_requires_auth(client):
    headers = {"Authorization": ""}
    response = await client.get("/items", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_items(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.get("/items", headers=headers)

    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert items[0]["name"] == "Test"
