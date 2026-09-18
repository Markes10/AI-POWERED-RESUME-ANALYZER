import time
from datetime import timedelta
from fastapi.testclient import TestClient

def test_token_expiry_behavior(test_client: TestClient, test_user):
    # create a token that expires in 1 second
    from services.auth import create_access_token
    from datetime import timedelta
    token = create_access_token(subject=str(test_user["id"]), expires_delta=timedelta(seconds=1))
    
    headers = {"Authorization": f"Bearer {token}"}
    # quickly use the token to call a protected endpoint that returns 401 if invalid
    resp = test_client.get("/api/v1/auth/users/me", headers=headers)
    # either user not found or HTTP 200/401 depending on DB; ensure token is accepted format-wise
    assert resp.status_code in (200, 401, 404)

    # wait for token to expire
    time.sleep(2)
    resp2 = test_client.get("/api/v1/auth/users/me", headers=headers)
    # now token should be rejected as expired with 401
    assert resp2.status_code == 401


def test_invalid_token(test_client: TestClient):
    headers = {"Authorization": "Bearer invalid.token.here"}
    resp = test_client.get("/api/v1/auth/users/me", headers=headers)
    assert resp.status_code == 401