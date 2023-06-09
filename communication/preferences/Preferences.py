#!/usr/bin/env python3

import random

from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value


class Preferences:
    """Preferences class.
    This class implements the preferences of an agent.

    attr:
        criterion_name_list: the list of criterion name (ordered by importance)
        criterion_value_list: the list of criterion value
    """

    def __init__(self):
        """Creates a new Preferences object.
        self.__criterion_name_list = preference between the criterions (i.e ecology > price > ... )
        self.__criterion_value_list = list of triplets (item, criterion, good/bad value)
        """
        self.__criterion_name_list = []
        self.__criterion_value_list = []

    def get_criterion_name_list(self) -> list[CriterionName]:
        """Returns the list of criterion name."""
        return self.__criterion_name_list

    def get_criterion_value_list(self) -> list[CriterionValue]:
        """Returns the list of criterion value."""
        return self.__criterion_value_list

    def get_sorted_criterion_value_list(self, reverse=False) -> list[CriterionValue]:
        """Returns the sorted list of criterion value, from most to least important."""
        return sorted(
            self.__criterion_value_list,
            key=lambda x: self.__criterion_name_list.index(x.get_criterion_name()),
            reverse=reverse,
        )

    def set_criterion_name_list(self, criterion_name_list: list[CriterionName]):
        """Sets the list of criterion name."""
        self.__criterion_name_list = criterion_name_list

    def add_criterion_value(self, criterion_value: list[CriterionValue]):
        """Adds a criterion value in the list."""
        self.__criterion_value_list.append(criterion_value)

    def get_value(self, item: Item, criterion_name: CriterionName) -> Value | None:
        """Gets the value for a given item and a given criterion name."""
        for value in self.__criterion_value_list:
            if (
                value.get_item() == item
                and value.get_criterion_name() == criterion_name
            ):
                return value.get_value()
        return None

    def is_preferred_criterion(self, criterion_name_1, criterion_name_2):
        """Returns if a criterion 1 is preferred to the criterion 2."""
        for criterion_name in self.__criterion_name_list:
            if criterion_name == criterion_name_1:
                return True
            if criterion_name == criterion_name_2:
                return False

    def is_preferred_item(self, item_1, item_2):
        """Returns True if the item 1 is preferred to the item 2."""
        return item_1.get_score(self) > item_2.get_score(self)

    def is_preferred_or_equal_item(self, item_1, item_2):
        """Returns True if the item 1 is preferred to the item 2."""
        return item_1.get_score(self) >= item_2.get_score(self)

    def most_preferred(self, item_list):
        """Returns the most preferred item from a list."""
        best_item = item_list[0]
        for item in item_list[1:]:
            if self.is_preferred_or_equal_item(item, best_item):
                if self.is_preferred_or_equal_item(best_item, item):
                    # both items are equally prefered
                    best_item = random.choice([best_item, item])
                else:
                    best_item = item
        return best_item

    def is_item_among_top_n_percent(self, item, item_list, n=50):
        """
        Return whether a given item is among the top n percent of the preferred items.

        :return: a boolean, True means that the item is among the favourite ones
        """
        # sort item list in descending order (preferred item will be [0])
        item_list.sort(key=lambda x: x.get_score(self), reverse=True)
        item_rank = item_list.index(item)
        return (item_rank) / len(item_list) < n / 100

    def sort_item_list_by_preference(self, item_list):
        # sort item list in descending order (preferred item will be [0])
        item_list.sort(key=lambda x: x.get_score(self), reverse=True)
        return item_list

    def __str__(self) -> str:
        result = f'Criterion order : {" > ".join([str(name) for name in self.get_criterion_name_list()])}\nCriterion values :\n'
        criterion_names = [str(name) for name in CriterionName]
        items = list(
            set(
                [
                    criterion_value.get_item()
                    for criterion_value in self.get_criterion_value_list()
                ]
            )
        )
        first_column_width = max([len(str(item)) for item in items])
        header = " " * first_column_width + "|" + "|".join(criterion_names)
        result += header + "\n"
        stars_columns_width = [max(len(name), 4) for name in criterion_names]
        rows = [str(item) for item in items]
        star_correspondance = {
            Value.VERY_BAD: "*",
            Value.BAD: "**",
            Value.GOOD: "***",
            Value.VERY_GOOD: "****",
        }
        for item in items:
            row = str(item) + " " * max(first_column_width - len(str(item)), 0)
            for i, criterion in enumerate(CriterionName):
                row += "|"
                value = self.get_value(item, criterion)
                if value is not None:
                    row += star_correspondance[value] + " " * max(
                        stars_columns_width[i] - len(star_correspondance[value]), 0
                    )
                else:
                    row += " " * stars_columns_width[i]
            row += " | " + str(item.get_score(self))
            result += row + "\n"
        return result


if __name__ == "__main__":
    """Testing the Preferences class."""
    agent_pref = Preferences()
    agent_pref.set_criterion_name_list(
        [
            CriterionName.PRODUCTION_COST,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
            CriterionName.NOISE,
        ]
    )

    diesel_engine = Item("Diesel Engine", "A super cool diesel engine", None)
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.PRODUCTION_COST, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.CONSUMPTION, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.DURABILITY, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.NOISE, Value.BAD)
    )

    electric_engine = Item("Electric Engine", "A very quiet engine", None)
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.PRODUCTION_COST, Value.BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.CONSUMPTION, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.DURABILITY, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(
            electric_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD
        )
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.NOISE, Value.VERY_GOOD)
    )

    """test list of preferences"""
    print(diesel_engine)
    print(electric_engine)
    print(diesel_engine.get_value(agent_pref, CriterionName.PRODUCTION_COST))
    print(
        agent_pref.is_preferred_criterion(
            CriterionName.CONSUMPTION, CriterionName.NOISE
        )
    )
    print(
        "Electric Engine > Diesel Engine : {}".format(
            agent_pref.is_preferred_item(electric_engine, diesel_engine)
        )
    )
    print(
        "Diesel Engine > Electric Engine : {}".format(
            agent_pref.is_preferred_item(diesel_engine, electric_engine)
        )
    )
    print(
        "Electric Engine (for agent 1) = {}".format(
            electric_engine.get_score(agent_pref)
        )
    )
    print(
        "Diesel Engine (for agent 1) = {}".format(diesel_engine.get_score(agent_pref))
    )
    print(
        "Most preferred item is : {}".format(
            agent_pref.most_preferred([diesel_engine, electric_engine]).get_name()
        )
    )
    print(
        "Diesel Engine in top 10% prefered : {}".format(
            agent_pref.is_item_among_top_10_percent(
                diesel_engine, [diesel_engine, electric_engine]
            )
        )
    )
    print(
        "Electric Engine in top 10% prefered : {}".format(
            agent_pref.is_item_among_top_10_percent(
                electric_engine, [diesel_engine, electric_engine]
            )
        )
    )
