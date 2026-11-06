"""Tests of input validation - correct and incorrect variants.

The tests never write to the database: they only check that valid data is
accepted by the validators and that malicious data is rejected.
"""
import pytest

from project import app
from project.books.models import Book
from project.customers.models import Customer
from project.validators import (
    ValidationError,
    validate_age,
    validate_book_name,
    validate_book_type,
    validate_person_name,
    validate_year_published,
)

XSS = '<script>alert(document.cookie)</script>'


@pytest.mark.parametrize('validator, value', [
    (validate_book_name, 'Pan Tadeusz'),
    (validate_person_name, 'J.R.R. Tolkien'),
    (validate_person_name, 'Anna Nowak-Żółtowska'),
    (validate_year_published, '1834'),
    (validate_book_type, '5days'),
    (validate_age, '42'),
])
def test_valid_input_is_accepted(validator, value):
    validator(value)  # must not raise


@pytest.mark.parametrize('validator, value', [
    (validate_book_name, XSS),
    (validate_book_name, '<img src=x onerror=alert(1)>'),
    (validate_book_name, ''),
    (validate_book_name, 'a' * 65),
    (validate_person_name, 'Jan123'),
    (validate_year_published, 3000),
    (validate_book_type, 'forever'),
    (validate_age, -1),
])
def test_invalid_input_is_rejected(validator, value):
    with pytest.raises(ValidationError):
        validator(value)


def test_book_with_xss_cannot_be_created():
    with pytest.raises(ValidationError):
        Book(name=XSS, author='Adam Mickiewicz', year_published=1834, book_type='5days')


def test_create_book_endpoint_rejects_xss():
    response = app.test_client().post('/books/create', json={
        'name': XSS, 'author': 'Adam Mickiewicz', 'year_published': '1834', 'book_type': '5days',
    })
    assert response.status_code == 400
    with app.app_context():
        assert Book.query.filter_by(name=XSS).first() is None


def test_create_customer_endpoint_rejects_xss():
    response = app.test_client().post('/customers/create', data={
        'name': 'Jan Kowalski', 'city': XSS, 'age': '30',
    })
    assert response.status_code == 400
    with app.app_context():
        assert Customer.query.filter_by(city=XSS).first() is None
