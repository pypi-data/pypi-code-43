
def learning_curves(history):
    """
    plot learning curves for each metric
    """
    metrics = [key for key in history.history.keys() if key != 'lr' and 'val' not in key]

    fig, ax_list = plt.subplots(1,len(metrics))
    p=0
    for metric in metrics:
        for train_val_label in ['','val_']:
            label = train_val_label+metric
            ax_list[p].plot(history.epoch, history.history[label], label = label)
        ax_list[p].set_xlabel('epoch')
        ax_list[p].set_ylabel(metric)
        ax_list[p].legend()
        p+=1
    fig.tight_layout(rect=(0,0,int(len(metrics)), int(len(metrics)/2)))
    plt.show()