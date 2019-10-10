class DeltaContract:
    """
    Base Wrapper to DeltaML smart contract

    """
    def __init__(self, contract, address=None):
        self._contract_caller = contract.caller
        self.address = address

    def get_functions(self):
        return self._contract_caller.all_functions()

    def exec(self):
        self._contract_caller.all_functions()

    def set_data_owner(self, address):
        self._contract_caller.setDataOwner(address)

    def set_federated_aggregator(self, address):
        self._contract_caller.setFederatedAggregator(address)

    def set_model_buyer(self, address):
        self._contract_caller.setModelBuyer(address)

    def get_improvement(self):
        return self._contract_caller.getImprovement()

    def calculate_fixed_payment(self, model_id, take, payees_count):
        return self._contract_caller.calculateFixedPayment(model_id, take, payees_count)

    def calculate_payment_for_validation(self, model_id):
        return self._contract_caller.calculatePaymentForValidation(model_id)

    def calculate_payment_for_orchestration(self, model_id):
        return self._contract_caller.calculatePaymentForOrchestration(model_id)


class FederatedAggregatorContract(DeltaContract):
    """
    Wrapper to Federated Aggregator contract functions
    """

    def __init__(self, contract, address):
        super().__init__(contract=contract, address=address)

    def new_model(self, model_id, validators, trainers, model_buyer):
        self._contract_caller(transaction={'from': self.address}).newModel(model_id, validators, trainers, model_buyer)

    def save_mse(self, model_id, mse, iter):
        self._contract_caller(transaction={'from': self.address}).saveMse(model_id, mse, iter)

    def save_partial_mse(self, model_id, mse, trainer, iter):
        self._contract_caller(transaction={'from': self.address}).savePartialMse(model_id, mse, trainer, iter)

    def calculate_contributions(self, model_id):
        self._contract_caller(transaction={'from': self.address}).calculateContributions(model_id)

    def pay_for_orchestration(self, model_id):
        self._contract_caller(transaction={'from': self.address}).payForOrchestration(model_id)


class ModelBuyerContract(DeltaContract):
    """
    Wrapper to Model Buyer contract functions
    """

    def __init__(self, contract, address):
        super().__init__(contract=contract, address=address)

    def pay_for_model(self, model_id, pay):
        self._contract_caller(transaction={'from': self.address}).payForModel(model_id, pay)

    def finish_model_training(self, model_id):
        self._contract_caller(transaction={'from': self.address}).finishModelTraining(model_id)

    def check_mse_for_iter(self, model_id, iter, mse):
        return self._contract_caller(transaction={'from': self.address}).checkMseForIter(model_id, iter, mse)

    def check_partial_mse_for_iter(self, model_id, trainer, iter, mse):
        return self._contract_caller(transaction={'from': self.address}).checkPartialMseForIter(model_id, trainer, iter, mse)


class DataOwnerContract(DeltaContract):
    """
    Wrapper to Data Owner contract functions
    """
    def __init__(self, contract, address):
        super().__init__(contract=contract, address=address)

    def get_do_contribution(self, model_id, data_owner_id):
        self._contract_caller(transaction={'from': self.address}).getDOContribution(model_id, data_owner_id)

    def calculate_payment_for_contribution(self, model_id, data_owner):
        return self._contract_caller(transaction={'from': self.address}).calculatePaymentForContribution(model_id, data_owner)

    def pay_for_contribution(self, model_id):
        self._contract_caller(transaction={'from': self.address}).payForContribution(model_id)

    def pay_for_validation(self, model_id):
        self._contract_caller(transaction={'from': self.address}).payForValidation(model_id)
