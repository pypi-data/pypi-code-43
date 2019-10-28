import pandas as pd

def best_scores(model, metric):
    res = model.evals_result_
    best = model.best_iteration_
    return (res["valid_1"][metric][best], res["training"][metric][best])