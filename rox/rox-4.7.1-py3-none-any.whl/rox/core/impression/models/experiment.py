class Experiment(object):
    def __init__(self, experiment):
        self.name = experiment.name
        self.identifier = experiment.id
        self.is_archived = experiment.is_archived
        self.labels = set(experiment.labels)

    def __str__(self):
        return '%s - %s' % (super(Experiment, self).__str__(), self.name)
