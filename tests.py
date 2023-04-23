from mesa import Model
from mesa.time import BaseScheduler

from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.Value import Value
from pw_argumentation import ArgumentAgent


def test1():
    list_items = [
        Item(
            "Diesel Engine",
            "A super cool diesel engine",
            {
                CriterionName.NOISE: 50,
            },
        ),
        Item(
            "Electric Engine",
            "A very quiet engine",
            {
                CriterionName.NOISE: 5,
            },
        ),
    ]

    model = ArgumentModel()

    A1 = ArgumentAgent(1, model, "A1", Preferences(), True)
    A2 = ArgumentAgent(2, model, "A2", Preferences())
    criterion_value_A1_1 = CriterionValue(
        list_items[0], CriterionName.NOISE, Value.VERY_GOOD
    )
    criterion_value_A1_2 = CriterionValue(list_items[1], CriterionName.NOISE, Value.BAD)
    A1.preferences = Preferences()
    A1.preferences.add_criterion_value(criterion_value_A1_1)
    A1.preferences.add_criterion_value(criterion_value_A1_2)
    A1.preferences.set_criterion_name_list([CriterionName.NOISE])
    A1.items = {item: None for item in list_items}

    criterion_value_A2_1 = CriterionValue(list_items[0], CriterionName.NOISE, Value.BAD)
    criterion_value_A2_2 = CriterionValue(
        list_items[1], CriterionName.NOISE, Value.VERY_GOOD
    )
    A2.preferences = Preferences()
    A2.preferences.add_criterion_value(criterion_value_A2_1)
    A2.preferences.add_criterion_value(criterion_value_A2_2)
    A2.preferences.set_criterion_name_list([CriterionName.NOISE])
    A2.items = {item: None for item in list_items}

    model.add_agents([A1, A2])
    for _ in range(10):
        model.step()


def test2():
    list_items = [
        Item(
            "Diesel Engine",
            "A super cool diesel engine",
            {
                CriterionName.NOISE: 5,
            },
        ),
        Item(
            "Electric Engine",
            "A very quiet engine",
            {
                CriterionName.NOISE: 5,
            },
        ),
    ]

    model = ArgumentModel()

    A1 = ArgumentAgent(1, model, "A1", Preferences(), True)
    A2 = ArgumentAgent(2, model, "A2", Preferences())
    criterion_value_A1_1 = CriterionValue(
        list_items[0], CriterionName.NOISE, Value.GOOD
    )
    criterion_value_A1_2 = CriterionValue(
        list_items[1], CriterionName.NOISE, Value.VERY_GOOD
    )
    A1.preferences = Preferences()
    A1.preferences.add_criterion_value(criterion_value_A1_1)
    A1.preferences.add_criterion_value(criterion_value_A1_2)
    A1.preferences.set_criterion_name_list([CriterionName.NOISE])
    A1.items = {item: None for item in list_items}

    criterion_value_A2_1 = CriterionValue(
        list_items[0], CriterionName.NOISE, Value.GOOD
    )
    criterion_value_A2_2 = CriterionValue(
        list_items[1], CriterionName.NOISE, Value.VERY_GOOD
    )
    A2.preferences = Preferences()
    A2.preferences.add_criterion_value(criterion_value_A2_1)
    A2.preferences.add_criterion_value(criterion_value_A2_2)
    A2.preferences.set_criterion_name_list([CriterionName.NOISE])
    A2.items = {item: None for item in list_items}

    model.add_agents([A1, A2])
    for _ in range(10):
        model.step()


def test3():
    list_items = [
        Item(
            "A",
            "A super cool diesel engine",
            {
                CriterionName.NOISE: 5,
            },
        ),
        Item(
            "B",
            "A very quiet engine",
            {
                CriterionName.NOISE: 5,
            },
        ),
        Item(
            "C",
            "So fast you can't even see it",
            {
                CriterionName.NOISE: 100,
            },
        ),
        Item(
            "D",
            "Lifts your whole family like a charm",
            {
                CriterionName.NOISE: 80,
            },
        ),
    ]

    model = ArgumentModel()

    A1 = ArgumentAgent(1, model, "X", Preferences(), True, rejection_threshold=70)
    A2 = ArgumentAgent(2, model, "Y", Preferences(), rejection_threshold=70)
    criterion_value_A1_1 = CriterionValue(
        list_items[0], CriterionName.NOISE, Value.VERY_GOOD
    )
    criterion_value_A1_2 = CriterionValue(
        list_items[1], CriterionName.NOISE, Value.GOOD
    )
    criterion_value_A1_3 = CriterionValue(list_items[2], CriterionName.NOISE, Value.BAD)
    criterion_value_A1_4 = CriterionValue(
        list_items[3], CriterionName.NOISE, Value.VERY_BAD
    )
    A1.preferences = Preferences()
    A1.preferences.add_criterion_value(criterion_value_A1_1)
    A1.preferences.add_criterion_value(criterion_value_A1_2)
    A1.preferences.add_criterion_value(criterion_value_A1_3)
    A1.preferences.add_criterion_value(criterion_value_A1_4)
    A1.preferences.set_criterion_name_list([CriterionName.NOISE])
    A1.items = {item: None for item in list_items}

    criterion_value_A2_1 = CriterionValue(
        list_items[0], CriterionName.NOISE, Value.VERY_BAD
    )
    criterion_value_A2_2 = CriterionValue(
        list_items[1], CriterionName.NOISE, Value.GOOD
    )
    criterion_value_A2_3 = CriterionValue(
        list_items[2], CriterionName.NOISE, Value.VERY_GOOD
    )
    criterion_value_A2_4 = CriterionValue(list_items[3], CriterionName.NOISE, Value.BAD)
    A2.preferences = Preferences()
    A2.preferences.add_criterion_value(criterion_value_A2_1)
    A2.preferences.add_criterion_value(criterion_value_A2_2)
    A2.preferences.add_criterion_value(criterion_value_A2_3)
    A2.preferences.add_criterion_value(criterion_value_A2_4)
    A2.preferences.set_criterion_name_list([CriterionName.NOISE])
    A2.items = {item: None for item in list_items}

    print(A1.preferences)
    print(A2.preferences)

    model.add_agents([A1, A2])
    for _ in range(10):
        model.step()


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self):
        self.schedule = BaseScheduler(self)
        self.__messages_service = MessageService(self.schedule)

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def add_agents(self, agents):
        for agent in agents:
            self.schedule.add(agent)


if __name__ == "__main__":
    # test1()
    # Expected result :
    # From 1 to 2 (PROPOSE) Diesel Engine
    # From 2 to 1 (REJECT) Diesel Engine
    # From 2 to 1 (PROPOSE) Electric Engine
    # From 1 to 2 (REJECT) Electric Engine
    # From 1 to 2 (COMMIT) None
    # From 2 to 1 (COMMIT) None

    # test2()
    # Expected result :
    # From 1 to 2 (PROPOSE) Electric Engine
    # From 2 to 1 (ACCEPT) Electric Engine
    # From 1 to 2 (COMMIT) Electric Engine
    # From 2 to 1 (COMMIT) Electric Engine

    test3()
    # Expected result :
    # From 1 to 2 (PROPOSE) A
    # From 2 to 1 (REJECT) A
    # From 2 to 1 (PROPOSE) C
    # From 1 to 2 (ASK_WHY) C
    # From 2 to 1 (ARGUE) Argument(C, NOISE = VERY_GOOD)
    # From 1 to 2 (ARGUE) Argument(not C, NOISE = BAD)
    # From 2 to 1 (ADMIT_DEFEAT) Argument(not C, NOISE = BAD)
    # From 2 to 1 (PROPOSE) B
    # From 1 to 2 (ACCEPT) B
    # From 2 to 1 (COMMIT) B
    # From 1 to 2 (COMMIT) B
