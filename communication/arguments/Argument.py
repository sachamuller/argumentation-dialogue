from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue


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
        self.item = item
        self.comparison_list = []
        self.couple_values_list = []

    def add_premiss_comparison(self, better_criterion, worse_criterion):
        self.comparison_list.append(Comparison(better_criterion, worse_criterion))

    def add_premiss_couple_value(self, couple_value: CoupleValue):
        self.couple_values_list.append(couple_value)

    def __str__(self):
        return (
            f"Argument({'not' if not self.boolean_decision else ''}"
            f"{'' if not self.comparison_list else ', '}"
            f"{self.item}{','.join(str(x) for x in self.comparison_list)}"
            f"{'' if not self.couple_values_list else ', '}"
            f"{','.join(str(x) for x in self.couple_values_list)})"
        )
