import requests
import pytest

def test_get_request():
    url = 'https://jsonplaceholder.typicode.com/posts/1'
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json()['id'] == 1

def test_post_request():
    url = 'https://jsonplaceholder.typicode.com/posts'
    data = {'title': 'foo', 'body': 'bar', 'userId': 1}
    response = requests.post(url, data=data)
    assert response.status_code == 201
    assert response.json()['title'] == 'foo'
    assert response.json()['body'] == 'bar'
    assert response.json()['userId'] == 1

def test_put_request():
    url = 'https://jsonplaceholder.typicode.com/posts/1'
    data = {'id': 1, 'title': 'foo', 'body': 'bar', 'userId': 1}
    response = requests.put(url, data=data)
    assert response.status_code == 200
    assert response.json()['title'] == 'foo'
    assert response.json()['body'] == 'bar'
    assert response.json()['userId'] == 1

def test_patch_request():
    url = 'https://jsonplaceholder.typicode.com/posts/1'
    data = {'title': 'foo'}
    response = requests.patch(url, data=data)
    assert response.status_code == 200
    assert response.json()['title'] == 'foo'

def test_delete_request():
    url = 'https://jsonplaceholder.typicode.com/posts/1'
    response = requests.delete(url)
    assert response.status_code == 200
    assert response.json() == {}