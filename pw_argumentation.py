import random
from typing import Iterable

from mesa import Model
from mesa.time import BaseScheduler

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.arguments.Argument import Argument
from communication.arguments.CoupleValue import CoupleValue
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.Value import Value
from enum import Enum


class Status(Enum):
    PROPOSED = 0  # transitory status
    ACCEPTABLE_MINIMUM = (
        1  # I won an argument arguing for it --> won't go below this item
    )
    IMPOSSIBLE = 2  # Rejected
    ARGUMENT_ENDED_WITH_DEFEAT = 3  # I lost an argument arguing against it

    # Si X convainc Y que non E : item devient IMPOSSIBLE pour les deux
    # Si X convainc Y que oui E : item devient ACCEPTABLE_MINIMUM pour X et ARGUMENT_ENDED_WITH_DEFEAT pour Y


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent."""

    def __init__(
        self,
        unique_id,
        model,
        name,
        preferences: Preferences,
        initiate_proposal=False,
        rejection_threshold: int = 80,
    ):
        super().__init__(unique_id, model, name)
        self.preferences = preferences
        self.items: dict[Item, Status | None] = {
            criterion.get_item(): None
            for criterion in self.preferences.get_criterion_value_list()
        }
        self.initiate_proposal = initiate_proposal
        self.available_arguments = {}
        self.used_counter_arguments = []
        self.is_done = False
        self.rejection_threshold = rejection_threshold

    def accept(self, item: Item, agent_id: int):
        self.simple_send_message(
            agent_id,
            MessagePerformative.ACCEPT,
            item,
        )

    def propose(self, item: Item, agent_id: int):
        self.items[item] = Status.PROPOSED
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
        self.is_done = True
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

    def reject(self, item, agent_id: int):
        self.items[item] = Status.IMPOSSIBLE
        self.simple_send_message(
            agent_id,
            MessagePerformative.REJECT,
            item,
        )

    def admit_defeat(self, argument: Argument, agent_id: int):
        if argument.boolean_decision:
            # the other argued for an item
            self.items[argument.item] = Status.ARGUMENT_ENDED_WITH_DEFEAT
        else:
            # the other argued agains an item
            self.items[argument.item] = Status.IMPOSSIBLE

        self.simple_send_message(
            agent_id,
            MessagePerformative.ADMIT_DEFEAT,
            argument,
        )

    def step(self):
        super().step()
        if self.is_done:
            return
        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.PROPOSE:
                # Find best non-impossible items over the minimal acceptable item
                acceptable_minimums = [
                    item
                    for (item, status) in self.items.items()
                    if status == Status.ACCEPTABLE_MINIMUM
                ]
                if len(acceptable_minimums) > 0:
                    most_preferred_acceptable_minimum = self.preferences.most_preferred(
                        acceptable_minimums
                    )
                    acceptable_items = [
                        item
                        for (item, status) in self.items.items()
                        if status != Status.IMPOSSIBLE
                        and self.preferences.is_preferred_item(
                            item, most_preferred_acceptable_minimum
                        )
                    ]
                else:
                    acceptable_items = [
                        item
                        for (item, status) in self.items.items()
                        if status != Status.IMPOSSIBLE
                    ]
                if len(acceptable_items) == 0:
                    # Il ne pourra jamais accepter l'item, mais il espère
                    # déconstruire les arguments de l'autre pour qu'il accepte enfin
                    # sa proposition préférée
                    self.ask_why(message.get_content(), message.get_exp())
                    continue

                if self.items[message.get_content()] is not None:
                    continue
                self.items[
                    message.get_content()
                ] = Status.PROPOSED  # Do not propose again

                if not self.preferences.is_item_among_top_n_percent(  # Si pas dans le top 10%, on le rejette
                    message.get_content(), list(self.items), n=self.rejection_threshold
                ):
                    self.reject(message.get_content(), message.get_exp())
                elif (  # Meilleur item non rejeté/contre-argumenté -> on accepte
                    self.preferences.most_preferred(acceptable_items)
                    == message.get_content()
                ):
                    self.accept(message.get_content(), message.get_exp())
                else:  # Sinon --> Ask why (commence une argumentation)
                    self.ask_why(message.get_content(), message.get_exp())

            elif message.get_performative() in (
                MessagePerformative.ACCEPT,
                MessagePerformative.COMMIT,
            ):
                if message.get_content() in self.items:
                    self.commit(message.get_content(), message.get_exp())

            elif message.get_performative() == MessagePerformative.ASK_WHY:
                item = message.get_content()
                argument = self.support_proposal(item, boolean_decision=True)
                self.argue(argument, message.get_exp())

            elif message.get_performative() == MessagePerformative.REJECT:
                self.items[message.get_content()] = Status.IMPOSSIBLE

            elif message.get_performative() == MessagePerformative.ADMIT_DEFEAT:
                argument = message.get_content()
                if argument.boolean_decision:
                    self.items[argument.item] = Status.ACCEPTABLE_MINIMUM
                else:
                    self.items[argument.item] = Status.IMPOSSIBLE

            elif message.get_performative() == MessagePerformative.ARGUE:
                argument: Argument = message.get_content()
                if (counter_argument := self.attack_argument(argument)) is not None:
                    self.argue(counter_argument, message.get_exp())
                elif (
                    counter_argument := self.support_proposal(argument.item, False)
                ) is not None:
                    self.argue(counter_argument, message.get_exp())
                else:
                    self.admit_defeat(argument, message.get_exp())

        # Make a new proposal
        if (
            len(messages) == 0
            and self.model.schedule.get_agent_count() > 0  # Au moins 2 agents
        ):
            acceptable_minimums = [
                item
                for (item, status) in self.items.items()
                if status == Status.ACCEPTABLE_MINIMUM
            ]
            if len(acceptable_minimums) > 0:
                most_preferred_acceptable_minimum = self.preferences.most_preferred(
                    acceptable_minimums
                )
                acceptable_proposals = [
                    item
                    for (item, status) in self.items.items()
                    if status in (None, Status.ARGUMENT_ENDED_WITH_DEFEAT)
                    and self.preferences.is_preferred_item(
                        item, most_preferred_acceptable_minimum
                    )
                ]
            else:
                acceptable_proposals = [
                    item
                    for (item, status) in self.items.items()
                    if status in (None, Status.ARGUMENT_ENDED_WITH_DEFEAT)
                ]
            other_agent = [
                agent for agent in self.model.schedule.agent_buffer() if agent != self
            ][0]
            if acceptable_proposals:  # Au moins 1 item disponible
                chosen_item = self.preferences.most_preferred(acceptable_proposals)
                if self.items[chosen_item] == Status.ARGUMENT_ENDED_WITH_DEFEAT:
                    # Si la meilleure proposition est un argument perdu, accepter car l'autre agent ne descendra pas plus bas
                    self.accept(chosen_item, other_agent.unique_id)
                else:
                    self.propose(chosen_item, other_agent.unique_id)
            else:  # Plus d'item disponible, impossible de trouver un accord
                self.commit(None, other_agent.unique_id)

    def generate_preferences(self, list_items: list[Item]):
        self.items = {item: None for item in list_items}
        # shuffle the criterions to get the order of preferences
        list_criterions = [criterion_name for criterion_name in CriterionName]
        random.shuffle(list_criterions)
        self.preferences.set_criterion_name_list(list_criterions)

        # for each criterion draw a random set of preferences and evaluate all the items according to it
        for criterion_name in CriterionName:
            criterion_range = criterion_name.criterion_range
            criterion_span = criterion_range[1] - criterion_range[0]
            three_p = [
                random.random() * criterion_span + criterion_range[0] for _ in range(3)
            ]
            three_p.sort()
            [p1, p2, p3] = three_p
            for item in list_items:
                if criterion_name in item.get_criterion_values().keys():
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

    def list_supporting_proposal(self, item: Item) -> list[Argument]:
        """
        Generate a list of premisses which can be used to support an item
        :param item: Item - name of the item
        return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        return self._list_proposal_with_given_values(
            item, [Value.GOOD, Value.VERY_GOOD]
        )

    def list_attacking_proposal(self, item: Item) -> list[Argument]:
        """
        Generate a list of premisses which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        return self._list_proposal_with_given_values(item, [Value.BAD, Value.VERY_BAD])

    def _list_proposal_with_given_values(
        self, item: Item, values_list: Iterable[Value]
    ) -> list[Argument]:
        """
        Generate a list of premisses which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        result = []
        for value_preference in self.preferences.get_sorted_criterion_value_list():
            if value_preference.get_item() == item:
                if value_preference.get_value() in values_list:
                    boolean_decision = values_list == [Value.GOOD, Value.VERY_GOOD]
                    argument = Argument(boolean_decision=boolean_decision, item=item)
                    argument.add_premiss_couple_value(
                        CoupleValue(
                            value_preference.get_criterion_name(),
                            value_preference.get_value(),
                        )
                    )
                    result.append(argument)
        return result

    def attack_argument(self, argument: Argument) -> Argument | None:
        """
        Use to find a counter-argument attacking a proposal
        :param argument: the argument to attack.
        :return: a counter-argument, or None if none exists.
        """
        item = argument.item
        counter_argument = Argument(
            boolean_decision=not argument.boolean_decision, item=item
        )
        for couple_value in argument.couple_values_list:
            # Counter argument on the value of an criterion
            own_value = self.preferences.get_value(item, couple_value.criterion_name)
            received_value_less_than_own_value: bool = (
                couple_value.value.value <= own_value.value
            )
            if (
                received_value_less_than_own_value and not argument.boolean_decision
            ) or (not received_value_less_than_own_value and argument.boolean_decision):
                counter_argument.add_premiss_couple_value(
                    CoupleValue(couple_value.criterion_name, own_value)
                )
                if counter_argument not in self.used_counter_arguments:
                    self.used_counter_arguments.append(counter_argument)
                    return counter_argument

            # Counter argument on the importance of an item

    def support_proposal(self, item: Item, boolean_decision: bool) -> Argument | None:
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: name of the item which was proposed
        :return: the strongest supportive argument
        """
        if not item in self.available_arguments:
            if boolean_decision:
                self.available_arguments[item] = self.list_supporting_proposal(item)
            else:
                self.available_arguments[item] = self.list_attacking_proposal(item)
        while len(self.available_arguments[item]) > 0 and (
            (argument := self.available_arguments[item].pop(0))
            not in self.used_counter_arguments
        ):
            self.used_counter_arguments.append(argument)
            return argument
        return None


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self, list_items):
        self.schedule = BaseScheduler(self)
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
                CriterionName.NOISE: 60,
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
                CriterionName.NOISE: 40,
            },
        ),
        Item(
            "Turbo Car",
            "So fast you can't even see it",
            {
                CriterionName.PRODUCTION_COST: 19784,
                CriterionName.CONSUMPTION: 8,
                CriterionName.DURABILITY: 2.5,
                CriterionName.ENVIRONMENT_IMPACT: 3,
                CriterionName.NOISE: 75,
            },
        ),
        Item(
            "Really Huge Truck",
            "Lifts your whole family like a charm",
            {
                CriterionName.PRODUCTION_COST: 15000,
                CriterionName.CONSUMPTION: 9.2,
                CriterionName.DURABILITY: 3.7,
                CriterionName.ENVIRONMENT_IMPACT: 3.7,
                CriterionName.NOISE: 80,
            },
        ),
    ]

    argument_model = ArgumentModel(list_items)
    print(argument_model.schedule.agents[0].preferences)
    print(argument_model.schedule.agents[1].preferences)
    for _ in range(100):
        argument_model.step()
