import pytest
from requests.sessions import Session

def test_request_with_unicode_method():
    session = Session()
    url = 'http://example.com'
    
    # Positive case with a valid unicode method
    response = session.request(u'GET', url)
    assert response.status_code == 200, "Expected status code 200 for GET request"
    
    # Positive case with a valid unicode method
    response = session.request(u'POST', url)
    assert response.status_code == 200, "Expected status code 200 for POST request"
    
    # Positive case with a valid unicode method
    response = session.request(u'PUT', url)
    assert response.status_code == 200, "Expected status code 200 for PUT request"
    
    # Positive case with a valid unicode method
    response = session.request(u'DELETE', url)
    assert response.status_code == 200, "Expected status code 200 for DELETE request"
    
    # Edge case: Empty method
    with pytest.raises(ValueError):
        session.request(u'', url)
    
    # Edge case: None method
    with pytest.raises(ValueError):
        session.request(None, url)
    
    # Edge case: Invalid method
    with pytest.raises(ValueError):
        session.request(u'INVALID_METHOD', url)

def test_request_with_non_ascii_method():
    session = Session()
    url = 'http://example.com'
    
    # Non-ASCII method
    with pytest.raises(ValueError):
        session.request(u'GET\u2022', url)
    
    # Non-ASCII method with a valid prefix
    with pytest.raises(ValueError):
        session.request(u'\u2022GET', url)

def test_request_with_unicode_url():
    session = Session()
    
    # Positive case with a valid unicode URL
    response = session.request(u'GET', u'http://example.com/\u2022')
    assert response.status_code == 200, "Expected status code 200 for GET request with unicode URL"
    
    # Edge case: Empty URL
    with pytest.raises(ValueError):
        session.request(u'GET', u'')

def test_request_with_non_ascii_url():
    session = Session()
    
    # Non-ASCII URL
    with pytest.raises(ValueError):
        session.request(u'GET', u'http://example.com/\u2022')
    
    # Non-ASCII URL with a valid prefix
    with pytest.raises(ValueError):
        session.request(u'GET', u'\u2022http://example.com/')