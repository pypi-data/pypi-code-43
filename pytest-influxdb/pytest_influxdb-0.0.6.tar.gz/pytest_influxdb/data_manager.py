import ast

from pytest_influxdb.test_result_dto import TestResultDTO
from pytest_influxdb.suite_result_dto import SuiteResultDTO


class DataManager:
    def save_db_data_in_properties(self, request, db_host, db_port, db_user, db_password, db_name,
                                   influxdb_values):
        request.node.user_properties = ({"influxdb": dict(influxdb_host=db_host, influxdb_port=db_port,
                                                          influxdb_user=db_user, influxdb_password=db_password,
                                                          influxdb_name=db_name, influxdb_values=influxdb_values)},)

    def get_test_result_dto(self, test_name, session_dict):
        test_result_dto_dict = session_dict.get('test_result_dto_session_dict')
        test_result_dto_dict.update({test_name: TestResultDTO()})
        test_result_dto: TestResultDTO = test_result_dto_dict.get(test_name)
        test_result_dto.set_test(test_name)
        return test_result_dto

    def get_report(self, request):
        try:
            report_outcome = request.node.rep_call
        except AttributeError:
            report_outcome = request.node.rep_setup
        return report_outcome

    def get_test_influxdb_components(self, influxdb, session_dict):
        influxdb_components = session_dict.get('influxdb')
        if not influxdb_components:
            session_dict.update({'influxdb': influxdb})
            influxdb_components = session_dict.get('influxdb')
        return influxdb_components

    def collect_custom_values(self, test_result_dto, influxdb_values):
        custom_values = influxdb_values
        if custom_values and custom_values is not '':
            influxdb_values_dict: dict = ast.literal_eval(str(custom_values))
            test_result_dto.set_field_values(test_result_dto.get_test(), influxdb_values_dict['fields']['test_result'])
            test_result_dto.set_tag_values(test_result_dto.get_test(), influxdb_values_dict['tags']['test_result'])

    def collect_user_properties(self, test_result_dto, request):
        user_properties_tuple = request.node.user_properties
        for var in user_properties_tuple:
            if isinstance(var, dict):
                test_result_dto.set_field_values(test_result_dto.get_test(), var)

    def generate_test_result_data(self, test_result_dto, project_name, release_version, run_id_value, report_outcome):
        test_result_dto.set_project(project_name)
        test_result_dto.set_version(release_version)
        test_result_dto.set_run(run_id_value)
        test_result_dto.set_duration_sec(report_outcome.duration)
        test_result_dto.set_status(report_outcome.outcome)
