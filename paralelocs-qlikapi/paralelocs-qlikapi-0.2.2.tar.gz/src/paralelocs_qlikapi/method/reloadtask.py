
from paralelocs_qlikapi.method.base import DefaultMethods
import json

class Task(DefaultMethods):
    """
    Classe para trabalhar com o recurso APP da API do QLIK

    """

    def __init__(self,
                 auth= None,
                 session=None):
        super().__init__(auth=auth, session=session)
        self.resource = 'reloadtask'

    def post(self):
        method = 'POST'
        resource = 'reloadtask/create'
        body = self.create_body_dict()
        data = json.dumps(body)
        return self.send(method = method, resource= resource, data=data)
       

        

    def create_composite_events_dict(self):
        compositeEvents = []
        compositeRules = []

        compositeRules.append(
                                dict(
                                        reloadTask= dict(id='6546fad6-e0e1-4bcd-8eaa-995e9cafe0c7'),
                                        ruleState = 1
                                    )
                            )
        union = dict(
                timeConstraint = dict(days=0, hours=0,minutes=360,seconds=0),
                compositeRules = compositeRules,
                name = "Event Trigger",
                enabled = True,
                eventType = 1
            )
        
        compositeEvents.append(union)

        return compositeEvents


    def create_task_dict(self):
        body = dict(
            
                    app= dict(
                                id= "1e048110-99a6-43d7-bac3-391070202967",
                                ), 
                    name="Reload Goto Analytics",
                    taskSessionTimeout= 1440,
                    maxRetries = 0,
                    enable= True
                    )
        return body

    def create_body_dict(self):

        body = dict(
            task = self.create_task_dict(),
            compositeEvents = self.create_composite_events_dict(),
            schemaEvents = self.create_schema_events_dict()
        )

        return body

    def create_schema_events_dict(self):
        schemaEvents = []
        schemaFilterDescription = ["* * - * * * * *"]

        body = dict(
            timeZone = "America/New_York",
            daylightSavingTime = 0,
            startDate = "2017-01-11T12:05:46.000",
            expirationDate = "9999-01-01T00:00:00.000",
            schemaFilterDescription = schemaFilterDescription,
            incrementDescription = "0 0 1 0",
            incrementOption = 2,
            name = "Daily",
            enabled = True
        )
        
        schemaEvents.append(body)

        return schemaEvents



    def reload(self, name):
        app = self.search(name=name)
        app = app['content'][0]
        appid = app['id']
        resource = f'app/{appid}/reload'
        method = 'POST'
        data = ''
        
        return self.send(method = method, resource= resource, data=data)