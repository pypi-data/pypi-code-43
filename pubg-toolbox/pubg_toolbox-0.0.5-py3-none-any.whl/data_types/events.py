class Event:
    def __init__(self, data):
        self.timestamp = data['_D']
        self.data_type = data['_T']
        self.process(data)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.get_type())

    def get_type(self):
        return self.data_type

    def process(self, data):
        pass

class AttackEvent(Event):
    def process(self, data):
        self.victim = data.get('victim')
        self.damage_reason = data.get('damageReason')
        self.damage_causer_name = data.get('damageCauserName')

class PlayerKillEvent(AttackEvent):
    pass

class PlayerMakeGroggyEvent(AttackEvent):
    pass
