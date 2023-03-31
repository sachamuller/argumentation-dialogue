from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue


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

    def add_premiss_couple_values(self, criterion_name, value):
        self.couple_values_list.append(CoupleValue(criterion_name, value))
