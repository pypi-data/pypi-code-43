from azure.devops.credentials import BasicAuthentication
from azure.devops.connection import Connection
from azure.devops.v5_0.work.models import TeamContext
from azure.devops.v5_1.client_factory import ClientFactoryV5_1
from azure.devops.v5_1.work_item_tracking import WorkItemTrackingClient 
from azure.devops.v5_1.work_item_tracking.models import Wiql
from pprint import pprint

class ProjectDTO(object):

    def __init__(self, project_id, teams):
        self.project_id = project_id
        self.teams = teams

class TFS(object):

    def __init__(self, personal_access_token, organization_url):

        self.credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=self.credentials)

        self.core_client = self.connection.clients.get_core_client()
        self.work_client = self.connection.clients_v5_1.get_work_client()
        self.work_item_tracking_client = self.connection.clients_v5_1.get_work_item_tracking_client()
        self.work_item_process_tracking_client = self.connection.clients_v5_1.get_work_item_tracking_process_client()
        

    def __create_team_context(self, project, team):
        return  TeamContext(project, project.id, team, team.id)
    
    def get_processes(self):
        return self.work_item_process_tracking_client.get_list_of_processes()

    def get_process_behaviors(self, process_id):
        return self.work_item_process_tracking_client.get_process_behaviors(process_id)
    
    def get_process_by_its_id(self, process_type_id):
        return self.work_item_process_tracking_client.get_process_by_its_id(process_type_id)
    
    def get_state_definitions(self, process_id):
        return self.work_item_process_tracking_client.get_state_definitions(process_id)

    def get_backlogs(self, project,team):
        team_context = self.__create_team_context(project, team)
        return self.work_client.get_backlogs(team_context)
    
    def get_work_item_types(self, project):
        return self.work_item_tracking_client.get_work_item_types(project)
    
    def get_work_items_project(self, project_id):
        return self.work_item_tracking_client.get_work_items(project_id)
    
    def get_work_item(self, work_item_id, project_id):
        return self.work_item_tracking_client.get_work_item(work_item_id,project_id)
    
    def get_work_item(self, work_item_id):
        return self.work_item_tracking_client.get_work_item(work_item_id)

    def get_backlog_work_items(self, project,team, backlog):
        team_context = self.__create_team_context(project, team)
        return self.work_client.get_backlog_level_work_items(team_context, backlog.id)

    def get_interactions(self, project, team):
        team_context = self.__create_team_context(project, team)
        return self.work_client.get_team_iterations(team_context)
    
    def get_work_item_query_by_wiql_epic_user_story_product_backlog_item(self):
        wiql = Wiql(
        query="""
                select [System.Id],
                    [System.WorkItemType],
                    [System.Title],
                    [System.State],
                    [System.AreaPath],
                    [System.IterationPath],
                    [System.Tags]
                from WorkItems
                where 
                [System.WorkItemType] == 'User Story' or 
                [System.WorkItemType] == 'Product Backlog Item' or 
                [System.WorkItemType] == 'Epic'
                order by [System.ChangedDate] desc"""
            )
        wiql_results = self.work_item_tracking_client.query_by_wiql(wiql).work_items
        if wiql_results:
            return wiql_results
        else:
            return []
    
    def get_work_item_query_by_wiql_task(self):
        wiql = Wiql(
        query="""
                select [System.Id],
                    [System.WorkItemType],
                    [System.Title],
                    [System.State],
                    [System.AreaPath],
                    [System.IterationPath],
                    [System.Tags]
                from WorkItems
                where 
                [System.WorkItemType] == 'Task'
                order by [System.ChangedDate] desc"""
            )
        wiql_results = self.work_item_tracking_client.query_by_wiql(wiql).work_items
        if wiql_results:
            return wiql_results
        else:
            return []
    
    
    def get_work_item_query_by_wiql(self):
        wiql = Wiql(
        query="""
                select [System.Id],
                    [System.WorkItemType],
                    [System.Title],
                    [System.State],
                    [System.AreaPath],
                    [System.IterationPath],
                    [System.Tags]
                from WorkItems
                order by [System.ChangedDate] desc"""
            )
        wiql_results = self.work_item_tracking_client.query_by_wiql(wiql).work_items
        if wiql_results:
            return wiql_results
        else:
            return []

    def get_iteration_work_items(self, project, team, interaction):
        team_context = self.__create_team_context(project, team)
        return self.work_client.get_iteration_work_items(team_context, interaction.id)

    def project_get_processes(self):
        return self.core_client.get_processes()

    def get_projects(self):
        projects = self.core_client.get_projects()
        return projects

    def get_teams(self, project_id):
        return self.core_client.get_teams(project_id)

    def get_team_members(self, project_id, team_id):
        
        return self.core_client.get_team_members_with_extended_properties(project_id=project_id,team_id=team_id)
        
    def get_all_team_project_organization(self):
       
        projects = self.core_client.get_projects()
        
        all_projects_teams = []

        for project in projects:
            teams = self.core_client.get_teams(project.id)
            project_DTO = ProjectDTO(project.id, teams)
            all_projects_teams.append (project_DTO)     
        
        return all_projects_teams
    
    def get_all_team_members_project(self):
        projects = self.core_client.get_projects()
        
        all_team_members = []

        # Show details about each project in the console
        for project in projects:
            teams = core_client.get_teams(project.id)
            for team in teams:
                team_members = core_client.get_team_members(project.id,team.id)
                for team_member in team_members:
                    team_member.additional_properties["team"] = team.id
                    all_team_members.append(team_member)
        return all_team_members
