from sqlalchemy import select, func
import pytest
import os
from dotenv import load_dotenv
from decimal import Decimal

from app.models import Product, User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

#
# prodcuts/create-product tests
#

create_product = [
    ("fooproduct", "", 10.99, 10, 201),
    ("fooproduct", "blablabla", 10.99, 10, 201),
    ("fooproduct", "", 0, 10, 201),
    ("", "", 10.99, 10, 422),
    ("fooproduct", "", -10.99, 10, 422),
    ("fooproduct", "", 10.99, -10, 422),
    ("fooproduct", "", 10.99, 0, 422),
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

def test_create_product_no_token(client):
    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    response = client.post("products/create-product", json=product_data)

    assert response.status_code == 401

def test_create_product_data_integrity(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    seller_id = test_session.scalar(select(User.id).where(User.name == "foo"))
    product = test_session.scalar(select(Product).where(Product.name == "foo"))

    assert product.description == "description"
    assert product.price == Decimal("10.99")
    assert product.quantity == 10
    assert product.seller_id == seller_id

#
# prodcuts/edit-product tests
#

edit_product = [
    ("foobar", "desc", "5.99", 200),
    ("foobar", None, None, 200),
    (None, "desc", None, 200),
    (None, None, "5.99", 200),
    (None, None, None, 200),
    ("F", None, None, 422),
    (None, None, -1.99, 422),
    (None, None, 0, 422)
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

def test_edit_product_no_token(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    edit_data = {"name": "foobar"}
    response = client.patch(f"products/edit-product?id={product_id}", json=edit_data)

    assert response.status_code == 401

def test_edit_product_empty_description(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product).where(Product.name == "foo")
    product = test_session.scalar(stmt)

    edit_data = {"description": ""}
    response = client.patch(f"products/edit-product?id={product.id}", json=edit_data, headers=headers)

    assert response.status_code == 200
    assert product.description == ""

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

def test_restock_product_doesnt_exist(client, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    restock_data = {"quantity": 10}
    response = client.patch("products/restock-product?id=100", json=restock_data, headers=headers)

    assert response.status_code == 404

def test_restock_product_missing_quantity(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    response = client.patch(f"products/restock-product?id={product_id}", json={}, headers=headers)

    assert response.status_code == 422

def test_restock_product_negative_success_data_integrity(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product).where(Product.name == "foo")
    product = test_session.scalar(stmt)

    restock_data = {"quantity": -5}
    response = client.patch(f"products/restock-product?id={product.id}", json=restock_data, headers=headers)

    assert response.status_code == 200
    assert product.quantity == 5

def test_restock_product_no_token(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    restock_data = {"quantity": 10}
    response = client.patch(f"products/restock-product?id={product_id}", json=restock_data)

    assert response.status_code == 401

#
# products/delete-listing tests
#

def test_delete_product(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    response = client.delete(f"products/delete-listing?id={product_id}", headers=headers)

    assert response.status_code == 200
    assert test_session.get(Product, product_id) is None

def test_delete_product_doesnt_exist(client, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.delete("products/delete-listing?id=100", headers=headers)

    assert response.status_code == 404

def test_delete_product_diffirent_seller(client, test_session, set_up_get_token):
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

    response = client.delete(f"products/delete-listing?id={product_id}", headers=headers_2)

    assert response.status_code == 403

def test_delete_product_no_token(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    response = client.delete(f"products/delete-listing?id={product_id}")

    assert response.status_code == 401

#
# products/{id} (get) tests
#

def test_get_product(client, test_session, set_up_get_token):
    token = set_up_get_token(name="foo", password="1234", email="foobar@gmail.com", role="seller")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    product_data = {"name": "foo", "description": "description", "price": 10.99, "quantity": 10}
    client.post("products/create-product", json=product_data, headers=headers)

    stmt = select(Product.id).where(Product.name == "foo")
    product_id = test_session.scalar(stmt)

    response = client.get(f"products/{product_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "foo"
    assert body["description"] == "description"
    assert Decimal(str(body["price"])) == Decimal("10.99")
    assert body["quantity"] == 10

def test_get_product_doesnt_exist(client):
    response = client.get("products/100")

    assert response.status_code == 404