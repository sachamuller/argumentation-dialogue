#!/usr/bin/env python3
from communication.preferences.CriterionName import CriterionName
from communication.preferences.Item import Item
from communication.preferences.Value import Value


class CriterionValue:
    """CriterionValue class.
    This class implements the CriterionValue object which associates an item with a CriterionName and a Value.
    """

    def __init__(self, item, criterion_name: CriterionName, value: Value):
        """Creates a new CriterionValue."""
        self.__item = item
        self.__criterion_name = criterion_name
        self.__value = value

    def get_item(self) -> Item:
        """Returns the item."""
        return self.__item

    def get_criterion_name(self) -> CriterionName:
        """Returns the criterion name."""
        return self.__criterion_name

    def get_value(self) -> Value:
        """Returns the value."""
        return self.__value

    def __str__(self) -> str:
        str(self.get_criterion_name())
        return f"{self.get_criterion_name()} value for {self.get_item()} : {self.get_value()} "
