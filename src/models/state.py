from enum import Enum


class UserState(int, Enum):
    NOT_CONFIRMED = 0
    ACTIVE = 1
    BLOCKED = 2
    DELETED = 3


class VacancyState(int, Enum):
    CLOSED = 0
    OPENED = 1


class VacancyType(int, Enum):
    PRACTICE = 0
    INTERNSHIP = 1


class TestType(int, Enum):
    THEORETICAL = 0
    PRACTICAL = 1
