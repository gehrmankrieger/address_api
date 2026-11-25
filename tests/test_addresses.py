"""API tests for the address endpoints."""

from fastapi.testclient import TestClient

RIZAL_PARK = {"street": "Roxas Blvd", "city": "Manila", "country": "Philippines",
              "latitude": 14.5831, "longitude": 120.9794}
MAKATI = {"street": "Ayala Ave", "city": "Makati", "country": "Philippines",
          "latitude": 14.5547, "longitude": 121.0244}
CEBU = {"street": "Osmeña Blvd", "city": "Cebu City", "country": "Philippines",
        "latitude": 10.3157, "longitude": 123.8854}


def create(client: TestClient, payload: dict) -> dict:
    """POST an address and return the created JSON."""
    response = client.post("/addresses", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_and_get(client: TestClient) -> None:
    created = create(client, {**RIZAL_PARK, "label": "  Park  "})
    assert created["id"] > 0
    assert created["label"] == "Park"  # whitespace stripped

    response = client.get(f"/addresses/{created['id']}")
    assert response.status_code == 200
    assert response.json()["city"] == "Manila"


def test_create_rejects_invalid_coordinates(client: TestClient) -> None:
    assert client.post("/addresses", json={**RIZAL_PARK, "latitude": 91}).status_code == 422
    assert client.post("/addresses", json={**RIZAL_PARK, "longitude": -181}).status_code == 422


def test_create_rejects_blank_and_missing_fields(client: TestClient) -> None:
    assert client.post("/addresses", json={**RIZAL_PARK, "city": "   "}).status_code == 422
    missing_street = {k: v for k, v in RIZAL_PARK.items() if k != "street"}
    assert client.post("/addresses", json=missing_street).status_code == 422


def test_list_is_paginated(client: TestClient) -> None:
    for payload in (RIZAL_PARK, MAKATI, CEBU):
        create(client, payload)
    page = client.get("/addresses", params={"skip": 1, "limit": 1}).json()
    assert [a["city"] for a in page] == ["Makati"]


def test_get_missing_returns_404(client: TestClient) -> None:
    assert client.get("/addresses/999").status_code == 404


def test_partial_update(client: TestClient) -> None:
    created = create(client, RIZAL_PARK)
    response = client.patch(f"/addresses/{created['id']}", json={"city": "Ermita"})
    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Ermita"
    assert body["street"] == RIZAL_PARK["street"]  # untouched


def test_update_rejects_null_and_empty(client: TestClient) -> None:
    created = create(client, RIZAL_PARK)
    assert client.patch(f"/addresses/{created['id']}", json={"city": None}).status_code == 422
    assert client.patch(f"/addresses/{created['id']}", json={}).status_code == 422


def test_delete(client: TestClient) -> None:
    created = create(client, RIZAL_PARK)
    assert client.delete(f"/addresses/{created['id']}").status_code == 204
    assert client.get(f"/addresses/{created['id']}").status_code == 404
    assert client.delete(f"/addresses/{created['id']}").status_code == 404


def test_nearby_in_range_sorted(client: TestClient) -> None:
    for payload in (CEBU, MAKATI, RIZAL_PARK):
        create(client, payload)

    response = client.get(
        "/addresses/nearby",
        params={"latitude": RIZAL_PARK["latitude"], "longitude": RIZAL_PARK["longitude"], "distance_km": 10},
    )
    assert response.status_code == 200
    results = response.json()
    assert [r["city"] for r in results] == ["Manila", "Makati"]  # Cebu (~570 km) excluded
    assert results[0]["distance_km"] == 0
    assert 0 < results[1]["distance_km"] <= 10


def test_nearby_validates_query(client: TestClient) -> None:
    params = {"latitude": 14.5, "longitude": 121.0, "distance_km": 0}
    assert client.get("/addresses/nearby", params=params).status_code == 422