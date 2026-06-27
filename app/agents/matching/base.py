from abc import ABC
from abc import abstractmethod


class MatchingAgent(

    ABC

):

    @abstractmethod
    def validate(

        self,

        payment,

        bank,

        score

    ):

        pass
