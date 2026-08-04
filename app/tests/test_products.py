from sqlalchemy import select, func
import pytest
import os
from dotenv import load_dotenv
from decimal import Decimal

from app.models import Product

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

#
# prodcuts/create-product tests
#

create_product = [
    ("fooproduct", "", 10.99, 10, 201),
    ("fooproduct", "blablabla", 10.99, 10, 201),
    ("", "", 10.99, 10, 422),
    ("fooproduct", "", -10.99, 10, 422),
    ("fooproduct", "", 10.99, -10, 422),
]

@pytest.mark.parametrize("name,description,price,quantity,expected", create_product)
def test_create_product(client, set_up_get_token, name, description, price, quantity, expected):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": name, "description": description, "price": price, "quantity": quantity}
    response = client.post("products/create-product", json=product_data, headers=headers)

    assert response.status_code == expected

def test_create_prodcut_not_seller(client, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="customer")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    response = client.post("products/create-product", json=product_data, headers=headers)

    assert response.status_code == 403

#
# prodcuts/edit-product tests
#

edit_product = [
    ("foobar", "desc", "5.99", 200),
    ("foobar", None, None, 200),
    (None, "desc", None, 200),
    (None, None, "5.99", 200),
    ("F", None, None, 422),
    (None, None, -1.99, 422)
]

@pytest.mark.parametrize("name,description,price,expected", edit_product)
def test_edit_product(client, test_session, set_up_get_token, name, description, price, expected):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    edit_data = {"name": name, "description": description, "price": price}
    response = client.patch(f"products/edit-product?id={product_id}", json=edit_data, headers=headers)

    assert response.status_code == expected

def test_edit_product_data_integrity(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    edit_data = {"name": "foobar", "description": "desc", "price": 5.99}
    client.patch(f"products/edit-product?id={product_id}", json=edit_data, headers=headers)

    product = test_session.get(Product, {product_id})

    assert product.name == "foobar"
    assert product.description == "desc"
    assert product.price == Decimal("5.99")

def test_edit_product_doesnt_exist(client, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    edit_data = {"name": "foobar", "description": "desc", "price": 5.99}
    response = client.patch(f"products/edit-product?id=100", json=edit_data, headers=headers)

    assert response.status_code == 404
    

def test_edit_product_diffirent_seller(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers_1 = {
        "Authorization": f"Bearer {token}"
    }

    token = set_up_get_token(name="foo2", password="1234", email="foobar2@gmail.com", role="seller")
    headers_2 = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers_1)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    edit_data = {"name": "foobar", "description": "desc", "price": 5.99}
    response = client.patch(f"products/edit-product?id={product_id}", json=edit_data, headers=headers_2)

    assert response.status_code == 403

#
# prodcuts/restock-product tests
#

restock_product = [
    (10, 200),
    (0, 400),
    (-20, 400)
]

@pytest.mark.parametrize("quantity,expected", restock_product)
def test_restock_product(client, test_session, set_up_get_token, quantity, expected):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    restock_data = {"quantity": quantity}
    response = client.patch(f"products/restock-product?id={product_id}", json=restock_data, headers=headers)

    assert response.status_code == expected

def test_restock_product_data_integrity(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product).where(Product.name == "foo")
    product = test_session.scalar(stmt)

    restock_data = {"quantity": 10}
    client.patch(f"products/restock-product?id={product.id}", json=restock_data, headers=headers)

    assert product.quantity == 20

def test_restock_product_diffirent_seller(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers_1 = {
        "Authorization": f"Bearer {token}"
    }

    token = set_up_get_token(name="foobar", password="1234", email="foo@gmail.com", role="seller")
    headers_2 = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers_1)

    stmt = select(Product).where(Product.name == "foo")
    product = test_session.scalar(stmt)

    restock_data = {"quantity": 10}
    response = client.patch(f"products/restock-product?id={product.id}", json=restock_data, headers=headers_2)

    assert response.status_code == 403

def test_restock_product_customer(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers_1 = {
        "Authorization": f"Bearer {token}"
    }

    token = set_up_get_token(name="foobar", password="1234", email="foo@gmail.com", role="customer")
    headers_2 = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers_1)

    stmt = select(Product).where(Product.name == "foo")
    product = test_session.scalar(stmt)

    restock_data = {"quantity": 10}
    response = client.patch(f"products/restock-product?id={product.id}", json=restock_data, headers=headers_2)

    assert response.status_code == 403