#!/usr/bin/env python3

from enum import Enum


class CriterionName(Enum):
    """CriterionName enum class.
    Enumeration containing the possible CriterionName.
    """

    # PRODUCTION_COST = 0, True, (8000, 20000)  # in euros
    # CONSUMPTION = 1, True, (0, 10)  # in L/100km
    # DURABILITY = 2, False, (1, 4)  # qualitative scale
    # ENVIRONMENT_IMPACT = 3, True, (1, 4)  # qualitative scale
    NOISE = 4, False, (30, 85)  # in dB

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(
        self, _: str, lower_is_better: bool = True, criterion_range: int = None
    ):
        self.__criterion_range = criterion_range
        self.__lower_is_better = lower_is_better

    def __str__(self):
        return str(self.name)

    # this is supposed to make sure that the criterion_range is read-only
    @property
    def criterion_range(self):
        return self.__criterion_range

    # same for lower_is_better
    @property
    def lower_is_better(self):
        return self.__lower_is_better
