from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue
from communication.preferences.Item import Item


class Argument:
    """
    Argument class.
    This class implements an argument used during ann interaction.

    attr:
        boolean_decision
        item
        comparison_list
        couple_values_list
    """

    def __init__(self, boolean_decision, item):
        self.boolean_decision = boolean_decision
        self.item: Item = item
        self.comparison_list: list[Comparison] = []
        self.couple_values_list: list[CoupleValue] = []

    def add_premiss_comparison(self, comparison: Comparison):
        self.comparison_list.append(comparison)

    def add_premiss_couple_value(self, couple_value: CoupleValue):
        self.couple_values_list.append(couple_value)

    def __str__(self):
        return (
            f"Argument({'not ' if not self.boolean_decision else ''}{self.item}"
            f"{'' if not self.comparison_list else ', '}"
            f"{','.join(str(x) for x in self.comparison_list)}"
            f"{'' if not self.couple_values_list else ', '}"
            f"{','.join(str(x) for x in self.couple_values_list)})"
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Argument)
            and self.boolean_decision == other.boolean_decision
            and self.item == other.item
            and self.comparison_list == other.comparison_list
            and self.couple_values_list == other.couple_values_list
        )
