class Chain:
    def __init__(self, document, chain, uuaa, author, modification, description, team, periodicity, execution_day,
                 time, criticality, reruns, interrelation_online, incompatibilities):
        self.document = document
        self.chain = chain
        self.uuaa = uuaa
        self.author = author
        self.modification = modification
        self.description = description
        self.team = team
        self.periodicity = periodicity
        self.execution_day = execution_day
        self.time = time
        self.criticality = criticality
        self.reruns = reruns
        self.interrelation_online = interrelation_online
        self.incompatibilities = incompatibilities
        self.dependencies = []
        self.jobs = []

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)

    def add_job(self, job):
        self.jobs.append(job)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        dependencies = "\n".join([str(dependency) for dependency in self.dependencies])
        jobs = "\n".join([str(job) for job in self.jobs])

        return (f"{self.__class__.__name__}\n"
                f"Document: {self.document}\n"
                f"Chain: {self.chain}\n"
                f"Uuaa: {self.uuaa}\n"
                f"Author: {self.author}\n"
                f"Modification: {self.modification}\n"
                f"Description:\n{self.description}\n\n\n"
                f"Team: {self.team}\n"
                f"Periodicity: {self.periodicity}\n"
                f"Execution_day: {self.execution_day}\n"
                f"Time: {self.time}\n"
                f"Criticality: {self.criticality}\n"
                f"Reruns: {self.reruns}\n"
                f"Interrelation_online: {self.interrelation_online}\n"
                f"Incompatibilities: {self.incompatibilities}\n\n"
                f"Dependencias:\n{dependencies}\n\n"
                f"Jobs:\n{jobs}\n\n\n")
        
        
class ChainDependency:

    def __init__(self, script_name, script_pre, chain_pre, script_post, chain_post):
        self.script_name = script_name
        self.script_pre = script_pre
        self.chain_pre = chain_pre
        self.script_post = script_post
        self.chain_post = chain_post

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"{self.__class__.__name__}\n"
                f"script_name: {self.script_name}\n"
                f"script_pre: {self.script_pre}\n"
                f"chain_pre: {self.chain_pre}\n"
                f"script_post: {self.script_post}\n"
                f"chain_post: {self.chain_post}\n")