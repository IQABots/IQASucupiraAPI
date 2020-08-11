import pytest
import json
import time

from api.server.settings import db
from api.server.models import UserModel, RevokedTokenModel


def register_user(client, username, password):
    return client.post(
        "/register",
        data=json.dumps(dict(username=username, password=password)),
        content_type="application/json",
    )


def login_user(client, username, password):
    return client.post(
        "/login",
        data=json.dumps(dict(username=username, password=password)),
        content_type="application/json",
    )


# ----------- Testes de registros -----------
def test_registration(client, init_db):
    """Testa cadastro de usuário no banco de dados"""
    response = register_user(client, username="test", password="testpwd")
    data = json.loads(response.data.decode())
    assert data["msg"] == "User test was registered"
    assert data["access_token"]
    assert data["refresh_token"]
    assert response.content_type == "application/json"
    assert response.status_code == 201


def test_registration_with_an_existing_account(client, init_db):
    """ Testa cadastro de usuário com nome de usuário já cadastrado"""
    user = UserModel(username="test", password="testpwd")
    init_db.session.add(user)
    init_db.session.commit()
    response = register_user(client, username="test", password="another-password")
    data = json.loads(response.data.decode())
    assert data["msg"] == "User already exists. Please Log in."
    assert response.content_type == "application/json"
    assert response.status_code == 202


# ---------- Testes de login -----------
def test_registered_user_login(client, init_db):
    """ Testa login de usuário previamente cadastrado"""
    user = UserModel(username="test", password="testpwd")
    init_db.session.add(user)
    init_db.session.commit()
    response = login_user(client, username="test", password="testpwd")

    data = json.loads(response.data.decode())
    assert data["msg"] == "Logged in as test"
    assert data["access_token"]
    assert data["refresh_token"]
    assert response.content_type == "application/json"
    assert response.status_code == 200


def test_non_registered_user_login(client, init_db):
    """ Testa login de um usuário não registrado """
    response = login_user(client, username="test", password="testpwd")
    data = json.loads(response.data.decode())
    assert data["msg"] == "User does not exist."
    assert response.content_type == "application/json"
    assert response.status_code == 404


def test_registered_user_login_with_incorrect_password(client, init_db):
    """ Testa login de usuário previamente cadastrado com senha errada"""
    user = UserModel(username="test", password="testpwd")
    init_db.session.add(user)
    init_db.session.commit()
    response = login_user(client, username="test", password="another-password")

    data = json.loads(response.data.decode())
    assert data["msg"] == "Incorrect password, please try again."
    assert response.content_type == "application/json"
    assert response.status_code == 401


# ------------- Testes de logout de tokens--------------------
def test_valid_logout_access(client, init_db):
    """ Testa logout de token de access válido """
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar access token válido
    response = client.post(
        "/logout/access",
        headers=dict(
            Authorization="Bearer "
            + json.loads(resp_register.data.decode())["access_token"]
        ),
    )
    data = json.loads(response.data.decode())
    assert data["msg"] == "Successfully logged out."
    assert response.status_code == 200


def test_valid_logout_refresh(client, init_db):
    """ Testa logout de token de refresh válido """
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar refresh token válido
    response = client.post(
        "/logout/refresh",
        headers=dict(
            Authorization="Bearer "
            + json.loads(resp_register.data.decode())["refresh_token"]
        ),
    )
    data = json.loads(response.data.decode())
    assert data["msg"] == "Successfully logged out."
    assert response.status_code == 200


def test_invalid_logout_access(client, init_db):
    """ Testa logout de token de access inválido """
    # Desconectar access token com token inválido
    response = client.post(
        "/logout/access",
        headers=dict(
            Authorization="Bearer access-token"
        ),
    )
    data = json.loads(response.data.decode())
    print(response.data.decode())
    assert data["msg"] == "Not enough segments"
    assert response.status_code == 422


def test_invalid_logout_refresh(client, init_db):
    """ Testa logout de token de refresh inválido """
    # Desconectar access token com token inválido
    response = client.post(
        "/logout/refresh",
        headers=dict(
            Authorization="Bearer refresh-token"
        ),
    )
    data = json.loads(response.data.decode())
    print(response.data.decode())
    assert data["msg"] == "Not enough segments"
    assert response.status_code == 422


def test_invalid_logout_access_with_refresh(client, init_db):
    """ Testa logout de token de access inválido """
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar access token com token inválido
    response = client.post(
        "/logout/access",
        headers=dict(
            Authorization="Bearer " 
            + json.loads(resp_register.data.decode())["refresh_token"]
        ),
    )
    data = json.loads(response.data.decode())
    print(response.data.decode())
    assert data["msg"] == "Only access tokens are allowed"
    assert response.status_code == 422


def test_invalid_logout_refresh_with_access(client, init_db):
    """ Testa logout de token de access inválido """
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar access token com token inválido
    response = client.post(
        "/logout/refresh",
        headers=dict(
            Authorization="Bearer " 
            + json.loads(resp_register.data.decode())["access_token"]
        ),
    )
    data = json.loads(response.data.decode())
    assert data["msg"] == "Only refresh tokens are allowed"
    assert response.status_code == 422


# ------------- Testes de atualização do token de acesso--------------------
def test_valid_refresh_token(client, init_db):
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar access token 
    response = client.post(
        "/logout/access",
        headers=dict(
            Authorization="Bearer " 
            + json.loads(resp_register.data.decode())["access_token"]
        ),
    )
    data = json.loads(response.data.decode())
    assert data["msg"] == "Successfully logged out."
    assert response.status_code == 200
    # Requisitar novo token de acesso
    response = client.post(
        "/refresh",
        headers=dict(
            Authorization="Bearer " 
            + json.loads(resp_register.data.decode())["refresh_token"]
        ),
    )
    data = json.loads(response.data.decode())
    assert data["access_token"]
    assert response.status_code == 200

def test_invalid_refresh_token(client, init_db):
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar access token com token inválido
    response = client.post(
        "/logout/access",
        headers=dict(
            Authorization="Bearer " 
            + json.loads(resp_register.data.decode())["access_token"]
        ),
    )
    data = json.loads(response.data.decode())
    assert data["msg"] == "Successfully logged out."
    assert response.status_code == 200
    # Requisitar novo token de acesso
    response = client.post(
        "/refresh",
        headers=dict(
            Authorization="Bearer refresh-token" 
        ),
    )
    data = json.loads(response.data.decode())
    assert data["msg"] == "Not enough segments"
    assert response.status_code == 422

# ------------- Testes do endpoint de busca-----------------------
def test_valid_search(client, init_db):
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Realizar consulta válida
    q = "Quais os artigos de computação com o tema inteligência artificial?"
    uid = mid = bid = 0
    resp_search = client.get(
        f"/search?q={q}&uid={uid}&mid={mid}&bid={bid}",
        headers=dict(
            Authorization="Bearer "
            + json.loads(resp_register.data.decode())["access_token"]
        )
    )
    data = json.loads(resp_search.data.decode())
    assert data["text"]
    assert type(data["results"]) == dict
    assert resp_search.status_code == 200

def test_invalid_search(client, init_db):
    # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Realizar consulta sem passar parametros
    resp_search = client.get(
        f"/search",
        headers=dict(
            Authorization="Bearer "
            + json.loads(resp_register.data.decode())["access_token"]
        )
    )
    data = json.loads(resp_search.data.decode())
    assert data["msg"] == "Parameter is missing in the query string."
    assert resp_search.status_code == 400


def test_valid_search_after_logout_access_token(client, init_db):
     # registrar usuário
    resp_register = register_user(
        client, username="test", password="testpwd"
    )
    data_register = json.loads(resp_register.data.decode())
    assert data_register["msg"] == "User test was registered"
    assert data_register["access_token"]
    assert data_register["refresh_token"]
    assert resp_register.content_type == "application/json"
    assert resp_register.status_code == 201
    # Desconectar access token válido
    resp_logout = client.post(
        "/logout/access",
        headers=dict(
            Authorization="Bearer "
            + json.loads(resp_register.data.decode())["access_token"]
        ),
    )
    data = json.loads(resp_logout.data.decode())
    assert data["msg"] == "Successfully logged out."
    assert resp_logout.status_code == 200
    # Realizar consulta
    q = "Quais os artigos de computação com o tema inteligência artificial?"
    resp_search = client.get(
       f"/search?q={q}",
        headers=dict(
            Authorization="Bearer "
             + json.loads(resp_register.data.decode())["access_token"]
        ),
    )
    data = json.loads(resp_search.data.decode())
    print(data)
    assert data["msg"] == "Token has been revoked"
    assert resp_search.status_code == 401
