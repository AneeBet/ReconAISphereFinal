from abc import ABC
from abc import abstractmethod


class CopilotAgent(ABC):

    @abstractmethod
    def chat(
        self,
        question,
        context
    ):
        pass
