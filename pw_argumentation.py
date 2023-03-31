import random
from typing import Iterable

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.arguments.Argument import Argument
from communication.arguments.CoupleValue import CoupleValue
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.Value import Value


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent."""

    def __init__(
        self, unique_id, model, name, preferences: Preferences, initiate_proposal=False
    ):
        super().__init__(unique_id, model, name)
        self.preferences = preferences
        self.items = [
            criterion.get_item()
            for criterion in self.preferences.get_criterion_value_list()
        ]
        self.initiate_proposal = initiate_proposal
        self.available_arguments = {}
        self.is_done = False

    def accept(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ACCEPT,
            item,
        )

    def propose(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.PROPOSE,
            item,
        )

    def ask_why(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ASK_WHY,
            item,
        )

    def commit(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.COMMIT,
            item,
        )
        # self.items.remove(item)

    def argue(self, argument, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ARGUE,
            argument,
        )

    def step(self):
        super().step()
        if self.is_done:
            return
        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.PROPOSE:
                if self.preferences.is_item_among_top_10_percent(
                    message.get_content(), self.items
                ):
                    self.accept(message.get_content(), message.get_exp())
                else:
                    self.ask_why(message.get_content(), message.get_exp())
            elif message.get_performative() in (
                MessagePerformative.ACCEPT,
                MessagePerformative.COMMIT,
            ):
                if message.get_content() in self.items:
                    self.commit(message.get_content(), message.get_exp())
                    self.is_done = True
            elif message.get_performative() == MessagePerformative.ASK_WHY:
                item = message.get_content()
                argument = Argument(boolean_decision=True, item=item)
                argument.add_premiss_couple_value(self.support_proposal(item))
                self.argue(argument, message.get_exp())

        # TODO: should be able to manage multiple proposals in parallel at a time
        if (
            len(messages) == 0
            and self.initiate_proposal  # Agent qui peut faire des propositions
            and self.model.schedule.get_agent_count() > 0  # Au moins 2 agents
            and len(self.items) > 0  # Au moins 1 item disponible
        ):
            other_agent = random.choice(
                [agent for agent in self.model.schedule.agent_buffer() if agent != self]
            )
            chosen_item = random.choice(self.items)
            self.propose(chosen_item, other_agent.unique_id)

    def generate_preferences(self, list_items: list[Item]):
        self.items = list_items.copy()
        # shuffle the criterions to get the order of preferences
        list_criterions = [criterion_name for criterion_name in CriterionName]
        random.shuffle(list_criterions)
        self.preferences.set_criterion_name_list(list_criterions)

        # for each criterion draw a random set of preferences and evaluate all the items according to it
        for criterion_name in CriterionName:
            criterion_range = criterion_name.criterion_range
            criterion_span = criterion_range[1] - criterion_range[0]
            p1 = (random.random() / 3) * criterion_span + criterion_range[0]
            p2 = (random.random() / 3 + 1 / 3) * criterion_span + criterion_range[0]
            p3 = (random.random() / 3 + 2 / 3) * criterion_span + criterion_range[0]
            for item in list_items:
                numerical_value = item.get_criterion_value(criterion_name)
                if numerical_value < p1:
                    criterion_value = CriterionValue(
                        item,
                        criterion_name,
                        Value.VERY_GOOD
                        if criterion_name.lower_is_better
                        else Value.VERY_BAD,
                    )
                elif numerical_value >= p1 and numerical_value < p2:
                    criterion_value = CriterionValue(
                        item,
                        criterion_name,
                        Value.GOOD if criterion_name.lower_is_better else Value.BAD,
                    )
                elif numerical_value >= p2 and numerical_value < p3:
                    criterion_value = CriterionValue(
                        item,
                        criterion_name,
                        Value.BAD if criterion_name.lower_is_better else Value.GOOD,
                    )
                elif numerical_value >= p3:
                    criterion_value = CriterionValue(
                        item,
                        criterion_name,
                        Value.VERY_BAD
                        if criterion_name.lower_is_better
                        else Value.VERY_GOOD,
                    )
                self.preferences.add_criterion_value(criterion_value)

    def send_message(self, message):
        super().send_message(message)
        print(message)

    def list_supporting_proposal(self, item: Item) -> list[CoupleValue]:
        """
        Generate a list of premisses which can be used to support an item
        :param item: Item - name of the item
        return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        return self._list_proposal_with_given_values(
            item, [Value.GOOD, Value.VERY_GOOD]
        )

    def list_attacking_proposal(self, item: Item) -> list[CoupleValue]:
        """
        Generate a list of premisses which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        return self._list_proposal_with_given_values(item, [Value.BAD, Value.VERY_BAD])

    def _list_proposal_with_given_values(
        self, item: Item, values_list: Iterable[Value]
    ) -> list[CoupleValue]:
        """
        Generate a list of premisses which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        result = []
        for value_preference in self.preferences.get_sorted_criterion_value_list():
            if value_preference.get_item() == item:
                if value_preference.get_value() in values_list:
                    result.append(
                        CoupleValue(
                            value_preference.get_criterion_name(),
                            value_preference.get_value(),
                        )
                    )
        return result

    def support_proposal(self, item: Item) -> CoupleValue | None:
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: name of the item which was proposed
        :return: the strongest supportive argument
        """
        if not item in self.available_arguments:
            self.available_arguments[item] = self.list_supporting_proposal(item)
        if len(self.available_arguments[item]) > 0:
            return self.available_arguments[item].pop(0)
        return None


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self, list_items):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        A1 = ArgumentAgent(1, self, "A1", Preferences(), True)
        A2 = ArgumentAgent(2, self, "A2", Preferences())
        A1.generate_preferences(list_items)
        A2.generate_preferences(list_items)
        self.schedule.add(A1)
        self.schedule.add(A2)

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()


if __name__ == "__main__":

    list_items = [
        Item(
            "Diesel Engine",
            "A super cool diesel engine",
            {
                CriterionName.PRODUCTION_COST: 12330,
                CriterionName.CONSUMPTION: 6.3,
                CriterionName.DURABILITY: 3.8,
                CriterionName.ENVIRONMENT_IMPACT: 4.8,
                CriterionName.NOISE: 65,
            },
        ),
        Item(
            "Electric Engine",
            "A very quiet engine",
            {
                CriterionName.PRODUCTION_COST: 17100,
                CriterionName.CONSUMPTION: 0,
                CriterionName.DURABILITY: 3,
                CriterionName.ENVIRONMENT_IMPACT: 2.2,
                CriterionName.NOISE: 48,
            },
        ),
    ]

    argument_model = ArgumentModel(list_items)
    print(argument_model.schedule.agents[0].preferences)
    print(argument_model.schedule.agents[1].preferences)
    for _ in range(15):
        argument_model.step()
