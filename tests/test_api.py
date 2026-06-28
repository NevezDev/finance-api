def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_and_protected_route(client):
    user = {
        "full_name": "Maria Silva",
        "email": "maria@example.com",
        "password": "senha123",
    }
    assert client.post("/api/auth/register", json=user).status_code == 200
    login = client.post(
        "/api/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert login.status_code == 200

    response = client.get(
        "/api/categories",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_financial_summary_and_goal_progress(client, auth_headers):
    category = client.post(
        "/api/categories",
        headers=auth_headers,
        json={"name": "Alimentacao", "type": "despesa", "color": "#ef4444"},
    )
    assert category.status_code == 200

    transactions = [
        {
            "description": "Salario",
            "type": "receita",
            "amount": 3000,
            "transaction_date": "2026-06-27",
        },
        {
            "category_id": category.json()["id"],
            "description": "Mercado",
            "type": "despesa",
            "amount": 500,
            "transaction_date": "2026-06-27",
        },
    ]
    for transaction in transactions:
        assert client.post(
            "/api/transactions", headers=auth_headers, json=transaction
        ).status_code == 200

    assert client.post(
        "/api/goals",
        headers=auth_headers,
        json={"title": "Reserva", "target_amount": 5000, "status": "ativa"},
    ).status_code == 200

    response = client.get("/api/reports/summary", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["total_income"] == 3000
    assert data["total_expenses"] == 500
    assert data["balance"] == 2500
    assert data["expenses_by_category"][0]["total"] == 500
    assert data["goals_progress"][0]["current_amount"] == 2500
    assert data["goals_progress"][0]["progress_percent"] == 50


def test_users_cannot_access_each_others_data(client, auth_headers):
    client.post(
        "/api/categories",
        headers=auth_headers,
        json={"name": "Privada", "type": "despesa"},
    )
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Outro Usuario",
            "email": "outro@example.com",
            "password": "senha123",
        },
    )
    login = client.post(
        "/api/auth/login",
        json={"email": "outro@example.com", "password": "senha123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get("/api/categories", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
