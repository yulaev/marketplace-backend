from sqlalchemy import select, func
import jwt
import os
from dotenv import load_dotenv

from app.models import User, UserRole

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

#
# users/sign-up tests 
#

def test_sign_up(client):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    response = client.post("users/sign-up", json=user_data)
    
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}

    user_data = {"name": "foo2", "password": "1234", "email": "foobar2@gmail.com", "role": "seller"}
    response = client.post("users/sign-up", json=user_data)
    
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}

def test_sign_up_data_integrity(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    stmt = select(User).where(User.name == "foo")
    user = test_session.scalar(stmt)
    
    assert user.name == "foo"
    assert user.email == "foobar@gmail.com"
    assert user.role == UserRole.customer
    assert user.password_hash != "1234"

def test_sign_up_duplicate_user(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)
    response = client.post("users/sign-up", json=user_data)

    assert response.status_code == 403
    
    stmt = select(func.count(User.id)).filter_by(name="foo")
    count = test_session.execute(stmt).scalar_one()
    
    assert count == 1

def test_sign_up_admin(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "admin"}
    response = client.post("users/sign-up", json=user_data)

    assert response.status_code == 403
    
    stmt = select(func.count(User.id)).filter_by(name="foo")
    count = test_session.execute(stmt).scalar_one()
    
    assert count == 0

#
# users/sign-in tests 
#

def test_sign_in_process(client):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    auth_data = {"username": "foo", "password": "1234"}
    response = client.post("users/sign-in", data=auth_data)

    body = response.json()
    assert body["token_type"] == "bearer"

    token = jwt.decode(body["access_token"], SECRET_KEY, algorithms=["HS256"])
    assert token["sub"] == "foo"

def test_auth_check_invalid_credentials(client):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    auth_data = {"username": "foo", "password": "1235"}
    response = client.post("users/sign-in", data=auth_data)

    assert response.status_code == 401

def test_auth_check_user_doesnt_exist(client):
    auth_data = {"username": "foo", "password": "1235"}
    response = client.post("users/sign-in", data=auth_data)

    assert response.status_code == 401

#
# users/edit-user tests 
#

def test_edit_user(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    stmt = select(User.id).where(User.name == "foo")
    user_id = test_session.scalar(stmt)

    auth_data = {"username": "foo", "password": "1234"}
    body = client.post("users/sign-in", data=auth_data)
    token_json = body.json()
    
    headers = {
        "Authorization": f"Bearer {token_json["access_token"]}"
    }
    
    edit_data = {"id": user_id, "name": "foobar", "email": "foo@gmail.com"}
    response = client.patch("users/edit-user", json=edit_data, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "User edited successfully"}

    user = test_session.get(User, user_id)

    assert user.name == "foobar"
    assert user.email == "foo@gmail.com"

def test_edit_user_other_than_yourself(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    stmt = select(User.id).where(User.name == "foo")
    user_id = test_session.scalar(stmt)

    user_data = {"name": "foobar", "password": "1234", "email": "foo@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)
    
    auth_data = {"username": "foobar", "password": "1234"}
    body = client.post("users/sign-in", data=auth_data)
    token_json = body.json()
    
    headers = {
        "Authorization": f"Bearer {token_json["access_token"]}"
    }
    
    edit_data = {"id": user_id, "name": "fooedit", "email": "fooedit@gmail.com"}
    response = client.patch("users/edit-user", json=edit_data, headers=headers)

    assert response.status_code == 403

def test_edit_user_doesnt_exist(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)
    
    auth_data = {"username": "foo", "password": "1234"}
    body = client.post("users/sign-in", data=auth_data)
    token_json = body.json()
    
    headers = {
        "Authorization": f"Bearer {token_json["access_token"]}"
    }
    
    edit_data = {"id": 100, "name": "foobar", "email": "foo@gmail.com"}
    response = client.patch("users/edit-user", json=edit_data, headers=headers)

    assert response.status_code == 404

#
# users/delete-user tests
#

def test_delete_user(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    stmt = select(User.id).where(User.name == "foo")
    user_id = test_session.scalar(stmt)
    
    auth_data = {"username": "foo", "password": "1234"}
    body = client.post("users/sign-in", data=auth_data)
    token_json = body.json()
    
    headers = {
        "Authorization": f"Bearer {token_json["access_token"]}"
    }
    
    response = client.delete(f"users/delete-user?id={user_id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}

    stmt = select(func.count(User.id)).where(User.id == user_id)
    count = test_session.scalar(stmt)

    assert count == 0

def test_delete_user_other_than_yourself(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    stmt = select(User.id).where(User.name == "foo")
    user_id = test_session.scalar(stmt)

    user_data = {"name": "foobar", "password": "1234", "email": "foo@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)
    
    auth_data = {"username": "foobar", "password": "1234"}
    body = client.post("users/sign-in", data=auth_data)
    token_json = body.json()
    
    headers = {
        "Authorization": f"Bearer {token_json["access_token"]}"
    }
    
    response = client.delete(f"users/delete-user?id={user_id}", headers=headers)

    assert response.status_code == 403

    stmt = select(func.count(User.id)).where(User.id == user_id)
    count = test_session.scalar(stmt)

    assert count == 1
    
def test_delete_user_doesnt_exist(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)
    
    auth_data = {"username": "foo", "password": "1234"}
    body = client.post("users/sign-in", data=auth_data)
    token_json = body.json()
    
    headers = {
        "Authorization": f"Bearer {token_json["access_token"]}"
    }
    
    response = client.delete("users/delete-user?id=100", headers=headers)

    assert response.status_code == 404

#
# users/ tests (GET)
#

def test_get_user(client, test_session):
    user_data = {"name": "foo", "password": "1234", "email": "foobar@gmail.com", "role": "customer"}
    client.post("users/sign-up", json=user_data)

    stmt = select(User.id).where(User.name == "foo")
    user_id = test_session.scalar(stmt)

    response = client.get(f"users/{user_id}")
    body = response.json()

    assert body["id"] == user_id
    assert body["name"] == "foo"
    assert body["email"] == "foobar@gmail.com"
    assert body["role"] == "customer"

def test_get_user_doesnt_exist(client):
    response = client.get(f"users/1")

    assert response.status_code == 404