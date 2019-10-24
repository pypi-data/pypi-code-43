class Job:
    def __init__(self, script, jobname, uuaa, support_group, origin_system, libreria_origen,
                 description, periodicity, sub_application, exectution_host, criticality):
        self.script = script
        self.jobname = jobname
        self.uuaa = uuaa
        self.support_group = support_group
        self.origin_system = origin_system
        self.libreria_origen = libreria_origen
        self.description = description
        self.periodicity = periodicity
        self.sub_application = sub_application
        self.exectution_host = exectution_host
        self.criticality = criticality
        self.filesanddb = []
        self.reruns_rules = []
        self.incompatibilities = []

    def add_filesanddb(self, file):
        self.filesanddb.append(file)

    def add_norma_rearranque(self, rerun_rule):
        self.reruns_rules.append(rerun_rule)

    def add_incompatibility(self, incompatibility):
        self.incompatibilities.append(incompatibility)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        filesanddb = "\n".join([str(fileanddb) for fileanddb in self.filesanddb])
        reruns_rules = "\n".join([str(rule) for rule in self.reruns_rules])
        incompatibilities = "\n".join([str(incompatibilidad) for incompatibilidad in self.incompatibilities])

        return (f"{self.__class__.__name__}\n"
                f"Script: {self.script}\n"
                f"Jobname: {self.jobname}\n"
                f"Uuaa: {self.uuaa}\n"
                f"Support_group: {self.support_group}\n"
                f"Origin_system: {self.origin_system}\n"
                f"Libreria_origen: {self.libreria_origen}\n"
                f"Description: {self.description}\n"
                f"Periodicity: {self.periodicity}\n"
                f"Sub_application: {self.sub_application}\n"
                f"Exectution_host: {self.exectution_host}\n"
                f"Criticality: {self.criticality}\n"
                f"Filesanddb:\n{filesanddb}\n\n"
                f"Reruns_rules:\n{reruns_rules}\n\n"
                f"Incompatibilities:\n{incompatibilities}\n\n")


class FileAndDb:

    def __init__(self, step, input_file, output_file, entities, access_type):
        self.step = step
        self.input = input_file
        self.output = output_file
        self.entities = entities
        self.access_type = access_type

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"{self.__class__.__name__}\n"
                f"Step: {self.step}\n"
                f"Input: {self.input}\n"
                f"Output: {self.output}\n"
                f"Entities: {self.entities}\n"
                f"Access_type: {self.access_type}\n")


class RerunRule:
    def __init__(self, step, before, after, reruns_rules):
        self.step = step
        self.before = before
        self.after = after
        self.reruns_rules = reruns_rules

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"{self.__class__.__name__}\n"
                f"Step: {self.step}\n"
                f"Before: {self.before}\n"
                f"After: {self.after}\n"
                f"Reruns_rules: {self.reruns_rules}\n")


class Incompatibility:
    def __init__(self, step, incompatibilities, criticality):
        self.step = step
        self.incompatibilities = incompatibilities
        self.criticality = criticality

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"{self.__class__.__name__}\n"
                f"Step: {self.step}\n"
                f"Incompatibilities: {self.incompatibilities}\n"
                f"Criticality: {self.criticality}\n")
