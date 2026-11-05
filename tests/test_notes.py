def create_note(client, title="First note", content="My note content"):
    return client.post("/notes", json={"title": title, "content": content})

def test_notes_require_authentication(client):
    assert client.get("/notes").status_code == 401
    assert create_note(client).status_code == 401

def test_create_and_list_notes(client, registered_user):
    created = create_note(client)
    assert created.status_code == 201
    note = created.get_json()["note"]
    assert note["title"] == "First note"

    listed = client.get("/notes?page=1&per_page=5")
    assert listed.status_code == 200
    body = listed.get_json()
    assert len(body["notes"]) == 1
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["total"] == 1

def test_show_update_delete_note(client, registered_user):
    note_id = create_note(client).get_json()["note"]["id"]

    shown = client.get(f"/notes/{note_id}")
    assert shown.status_code == 200

    updated = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert updated.status_code == 200
    

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.get_json()["note"]["title"] == "Updated"

    deleted = client.delete(f"/notes/{note_id}")
    assert deleted.status_code == 204

    assert client.get(f"/notes/{note_id}").status_code == 404


def test_users_cannot_access_each_others_notes(client, app):
    create_note(client, "Alice note", "Private")
    client.post("/logout")
    client.post("/signup", json={"username": "bob", "password": "password123"})

    assert client.get("/notes").get_json()["pagination"]["total"] == 0

    assert client.get("/notes/1").status_code == 404
    assert client.patch("notes/1", json={"title": "Stolen"}).status_code == 404
    assert client.delete("/notes/1").status_code == 404

def test_pagination(client, registered_user):
    for index in range(3):
        response = create_note(client, f"Note {index}", f"Content {index}")
        assert response.status_code == 201

    first_page = client.get("/notes?page=1&per_page=2").get_json()
    assert len(first_page["notes"]) == 2
    assert first_page["pagination"]["pages"] == 2
    assert first_page["pagination"]["has_next"] is True

