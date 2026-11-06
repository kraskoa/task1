"""Input validation for domain objects (Book, Customer, Loan).

Validation follows a whitelist approach: every text field has an explicit set
of allowed characters, so HTML/JavaScript metacharacters such as ``<``, ``>``,
``=`` or ``/`` are rejected before an object can be created or modified.
The functions are hooked into the models with SQLAlchemy's ``@validates``,
so every assignment (constructor, edit endpoints, loan return) is checked.
"""
import re
from datetime import date


class ValidationError(ValueError):
    """Raised when user supplied data does not satisfy the validation rules."""


MAX_TEXT_LENGTH = 64  # matches db.String(64) columns

# Book title: Unicode letters, digits, space and basic punctuation.
_TITLE_RE = re.compile(r"[\w .,:;!?'\"()&-]+")

# Person names and city names: must start with a Unicode letter, then letters,
# space, dot, apostrophe or hyphen ("J.R.R. Tolkien", "O'Neil", "Bielsko-Biała").
_NAME_RE = re.compile(r"[^\W\d_]+(?:[ .'-]+[^\W\d_]+)*\.?")

BOOK_TYPES = frozenset({'2days', '5days', '10days'})

MIN_AGE, MAX_AGE = 1, 120


def _validate_text(value, field, pattern, max_length=MAX_TEXT_LENGTH):
    if not isinstance(value, str):
        raise ValidationError(f'{field} is required and must be text')
    value = value.strip()
    if not value:
        raise ValidationError(f'{field} must not be empty')
    if len(value) > max_length:
        raise ValidationError(f'{field} must be at most {max_length} characters long')
    if not pattern.fullmatch(value):
        raise ValidationError(f'{field} contains forbidden characters')
    return value


def _validate_int(value, field, minimum, maximum):
    # bool is a subclass of int - reject it explicitly
    if isinstance(value, bool):
        raise ValidationError(f'{field} must be an integer')
    if isinstance(value, str):
        if not re.fullmatch(r'\d{1,4}', value.strip()):
            raise ValidationError(f'{field} must be an integer')
        value = int(value)
    if not isinstance(value, int):
        raise ValidationError(f'{field} must be an integer')
    if not minimum <= value <= maximum:
        raise ValidationError(f'{field} must be between {minimum} and {maximum}')
    return value


def validate_book_name(value):
    return _validate_text(value, 'Book name', _TITLE_RE)


def validate_person_name(value, field='Name'):
    return _validate_text(value, field, _NAME_RE)


def validate_city(value):
    return _validate_text(value, 'City', _NAME_RE)


def validate_year_published(value):
    return _validate_int(value, 'Year published', 1, date.today().year)


def validate_book_type(value):
    if value not in BOOK_TYPES:
        raise ValidationError(f'Book type must be one of: {", ".join(sorted(BOOK_TYPES))}')
    return value


def validate_age(value):
    return _validate_int(value, 'Age', MIN_AGE, MAX_AGE)
