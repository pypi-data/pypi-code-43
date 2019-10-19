from pydal import DAL, Field
import os
from types import MethodType
import pandas as pd
from datetime import datetime
import shutil
from ..utils.defaultlog import log

def get_db():
    """ return database connection """
    # define database
    log.info("loading database connection")
    data = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/db"
    os.makedirs(data, exist_ok=True)
    db = DAL('sqlite://db', folder=data)

    # table definitions ######################################################
    """
    job:      job pipe
    name:     output filename    
    status:   pending, waiting, ready,
              loading, running, saving,
              completed, failed, failed_missing, failed_upstream
    details:  list of waiting tasks; or error message
    process:  name of process on which it ran
    started:  time run started
    finished: time run finished
    task:     pickled task
    """
    db.define_table("task",
                    Field("url"),
                    Field("job"),
                    Field("name"),
                    Field("status"),
                    Field("details"),
                    Field("process"),
                    Field("started", "datetime"),
                    Field("finished", "datetime"),
                    Field("progress", "integer"),
                    Field("task", "blob"))

    """
    task:      task id that is waiting
    awaiting:  input url that is not available yet
    """
    db.define_table("waiting",
                    Field("task", "reference task"),
                    Field("awaiting"))

    # extensions to db ##########################################################

    def df(db, table):
        """ return table as pandas dataframe """
        # load data
        rows = db(db[table]).select()
        df = pd.DataFrame.from_dict(rows.as_dict(), orient="index")

        # add name and format for any columns with no data
        for col in list(set(db[table].fields) - set(df.columns)):
            df[col] = None
        for field in db[table]:
            if field.type == "datetime":
                df[field.name] = pd.to_datetime(df[field.name])
            # add other types here as needed
        return df
    db.df =MethodType(df, db)

    def taskview(db):
        """ return formatted view of task table """
        df = db.df("task")
        df["elapsed_mins"] = (df.finished.fillna(datetime.now()) - df.started).dt.total_seconds() // 60
        df.started = df.started.dt.strftime("%H:%M").str.replace("NaT", "")
        df.finished = df.finished.dt.strftime("%H:%M").str.replace("NaT", "")
        df = df.drop(["task"], axis=1)
        df = df.fillna("")
        df.progress = df[df.progress!=""].progress.apply(lambda x: str(int(x))+"%")
        df = df[["id", "url", "job", "name", "status", "process",
                 "started", "finished", "elapsed_mins", "progress", "details"]]
        df = df.set_index("id", drop=True)
        return df
    db.taskview = MethodType(taskview, db)

    def delete_tables(db):
        """ delete all tables """
        db(db.task).delete()
        db(db.waiting).delete()
        db.commit()
    db.delete_tables = MethodType(delete_tables, db)

    def delete(db):
        """ delete database folder """
        shutil.rmtree(db.as_dict()["folder"])
    db.delete = MethodType(delete, db)

    return db

db = get_db()