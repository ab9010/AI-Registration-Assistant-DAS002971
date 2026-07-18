import app as web_app


def test_health_endpoint():
    client = web_app.app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['task_id'] == 'AI-SS-001'


def test_chat_api_starts_registration():
    client = web_app.app.test_client()
    response = client.post('/api/chat', json={'message': 'Register me'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['state'] == 'await_name'
    assert payload['progress'] == 10
