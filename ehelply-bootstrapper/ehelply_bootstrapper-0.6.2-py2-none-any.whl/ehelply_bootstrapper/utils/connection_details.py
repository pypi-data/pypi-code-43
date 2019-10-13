from pydantic import BaseModel


class ConnectionDetails(BaseModel):
    """
    Holds the host, port, username, and password for some connection

    ...

    Attributes
    ----------
    host : str
        Holds the connection host. Typically localhost in development, and the docker alias in production
    port : int
        Holds the port
    username : str
        Holds the username
    password : str
        Holds the password
    """
    host: str
    port: int
    username: str
    password: str
