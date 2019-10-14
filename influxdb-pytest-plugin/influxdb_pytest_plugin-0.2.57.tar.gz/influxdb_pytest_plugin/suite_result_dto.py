class SuiteResultDTO:
    __run = 'UNDEFINED'
    __project = 'UNDEFINED'
    __version = 'UNDEFINED'
    __passed = None
    __failed = None
    __skipped = None
    __duration_sec = 0
    __disabled = 0
    __retries = 0
    __suite_result_dict = {'tags': {}, 'fields': {}}

    def get_run(self):
        return self.__run

    def set_run(self, run):
        self.__run = str(run)

    def get_project(self):
        return self.__project

    def set_project(self, project):
        self.__project = str(project)

    def get_version(self):
        return self.__version

    def set_version(self, version):
        self.__version = str(version)

    def get_passed(self):
        return self.__passed

    def set_passed(self, passed):
        self.__passed = int(passed)

    def get_failed(self):
        return self.__failed

    def set_failed(self, failed):
        self.__failed = int(failed)

    def get_skipped(self):
        return self.__skipped

    def set_skipped(self, skipped):
        self.__skipped = int(skipped)

    def get_duration_sec(self):
        return self.__duration_sec

    def set_duration_sec(self, duration_sec):
        self.__duration_sec = int(duration_sec)

    def get_disabled(self):
        return self.__disabled

    def set_disabled(self, disabled):
        self.__disabled = int(disabled)

    def get_retries(self):
        return self.__retries

    def set_retries(self, retries):
        self.__retries = int(retries)

    def get_suite_result_dict(self):
        return SuiteResultDTO.__suite_result_dict

    def set_suite_result_dict(self, suite_result_dict):
        SuiteResultDTO.__suite_result_dict = suite_result_dict

    def get_suite_json(self, measurement_name):
        json_body = [
            {
                "measurement": measurement_name,
                "tags": {
                    "run": self.__run,
                    "project": self.__project,
                    "version": self.__version
                },
                "fields": {
                    "pass": self.__passed,
                    "fail": self.__failed,
                    "skip": self.__skipped,
                    "duration_sec": self.__duration_sec,
                    "retries": self.__retries,
                    "disabled": self.__disabled
                }
            }
        ]

        tags_dict = SuiteResultDTO.__suite_result_dict['tags']
        for key in tags_dict:
            suite_tags = json_body[0]['tags']
            suite_tags.update({key: tags_dict[key]})
        fields_dict = SuiteResultDTO.__suite_result_dict['fields']
        for key in fields_dict:
            suite_fields = json_body[0]['fields']
            suite_fields.update({key: fields_dict[key]})

        return json_body

    def set_tag_values(self, tags_dict):
        suite_tags = SuiteResultDTO.__suite_result_dict
        suite_tags['tags'].update(tags_dict)

    def set_field_values(self, fields_dict):
        suite_fields = SuiteResultDTO.__suite_result_dict
        suite_fields['fields'].update(fields_dict)
