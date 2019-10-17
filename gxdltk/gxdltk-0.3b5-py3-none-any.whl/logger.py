"""
logging in deep learning
"""

def logger(train_logs: dict, test_logs:dict, file:str="", **kwargs):
    """
    Args:
        logs: dict type, must have key "test" or "train"
        file: path file

    Returns: None

    """
    for k in kwargs.keys():
        print(f"{k} is {kwargs[k]}")
    print("---------------Train---------------")
    for k in train_logs.keys():
        print(f"Training {k} is {train_logs[k]}")
    print("---------------Test---------------")
    for k in test_logs.keys():
        print(f"Testing {k} is {test_logs[k]}")

    if len(file) != 0:
        with open(file,'w') as fp:
            for k in train_logs.keys():
                print(f"Training {k} is {train_logs[k]}", file=fp)
            for k in test_logs.keys():
                print(f"Testing {k} is {test_logs[k]}", file=fp)
    print("End logs")
