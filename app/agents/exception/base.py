from abc import ABC
from abc import abstractmethod


class ExceptionAnalysisAgent(ABC):

    @abstractmethod
    def analyze(
        self,
        reconciliation,
        payment_transaction,
        bank_transaction
    ):
        pass
