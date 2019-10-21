import matplotlib.pyplot as plt
import pandas as pd 
import seaborn as sns

def plot_importance(reg, df: pd.DataFrame, depth: int):
    feature_imp = pd.DataFrame(sorted(zip(reg.feature_importances_,df.columns)), columns=['Value','Feature'])[-30:]
    plt.figure(figsize=(14, 7))
    sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False))