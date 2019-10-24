from crawling_gocd.gocd_domain import Pipeline

class Calculator:
    def __init__(self, strategyHandlers):
        self.strategyHandlers = strategyHandlers

    def work(self, pipelines: Pipeline, results = []):
        for handler in self.strategyHandlers:
            handler.calculate(pipelines, results)
        return results
