from datetime import datetime
from ehelply_bootstrapper.models.mongo import MongoModel


class ServiceModel(MongoModel):
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    deleted_at: datetime = None
