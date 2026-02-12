def test_items_requires_auth(client):
    response = client.get("/items")
    assert response.status_code == 403
