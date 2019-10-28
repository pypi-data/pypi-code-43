import pandas as pd

def best_scores(model, metric):
    res = model.evals_result()
    best = model.best_iteration
    return (res["validation_1"][metric][best], res["validation_0"][metric][best])

def clear_gpu(model):
    try:
        model.get_booster().__del__()
    except: 
            pass

def best_n_feats(model, n):
    return list(pd.DataFrame(
        model.get_booster().get_score().items(), 
        columns=['feature','importance'],
    ).sort_values('importance', ascending=False).head(n)["feature"].values)
