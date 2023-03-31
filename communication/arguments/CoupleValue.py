from communication.preferences.CriterionName import CriterionName


class CoupleValue:
    def __init__(self, criterion_name: CriterionName, value):
        self.criterion_name = criterion_name
        self.value = value

    def __str__(self) -> str:
        return f"{self.criterion_name} = {self.value}"
