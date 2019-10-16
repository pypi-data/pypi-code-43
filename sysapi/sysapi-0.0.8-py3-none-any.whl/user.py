from typing import List, Optional
from pydantic import BaseModel
from pydantic.types import EmailStr




## Safer users are valid system users, created in group "users" with 

class UserModel(BaseModel):
    login: str
    active: bool = True



## Based on tutorial example at 
## https://fastapi.tiangolo.com/tutorial/extra-models/
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str = None

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str = None

## TODO: Move this to unit tests...
test_users = [ ]

for user in ['victor', 'edouard', 'paul']:
    test_users.append(UserInDB(username=user, email=user+'@example.com', full_name=user.capitalize()+' Fullnamed', hashed_password='whetever' ))


def get_users()->List[str]:
    return [u.username for u in test_users]

def get_user(login: str)-> Optional[UserInDB]:
    return next((u for u in test_users if u.username == login), None)

def exists_user(user_in: UserIn) -> bool:
    for u in test_users: 
        if u.username == user_in.username: return True
    return False

def create_user(user_in: UserIn) -> Optional[UserInDB]:
    if not exists_user(user_in):
        new_user = UserInDB(**user_in.dict(), hashed_password='whetever'+user_in.password)
        test_users.append(new_user)
        return new_user
    return None
