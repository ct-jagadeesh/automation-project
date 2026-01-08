import requests
from jsonschema import validate

USERS_API = "https://jsonplaceholder.typicode.com/users"

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string"},
        "address": {"type": "object"},
    },
    "required": ["id", "name", "email"]
}

def test_users_api_contract():
    response = requests.get(USERS_API, timeout=10)
    assert response.status_code == 200

    users = response.json()
    assert len(users) > 0

    # Validate contract of first user
    validate(instance=users[0], schema=USER_SCHEMA)

    print("[PASS] Users API contract validated")
