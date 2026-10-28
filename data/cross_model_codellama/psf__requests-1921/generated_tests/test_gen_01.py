from requests import Session

def test_session():
    with Session() as session:
        response = session.get("http://www.example.com")
        assert response.status_code == 200