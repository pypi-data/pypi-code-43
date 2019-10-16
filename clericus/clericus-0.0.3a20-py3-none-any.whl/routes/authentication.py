from ..handler import Method, Endpoint, newMethod
from ..parsing import (
    RequestParser,
    DictParser,
    ResponseSerializerWithErrors,
)
from ..parsing.fields import (
    NonBlankStringField,
    EmailField,
    StringField,
    UsernameField,
    Field,
    DictField,
    ListField,
)

from ..schemas.user import createUser

from ..schemas.authentication import authenticateUser
from ..middleware import setCurrentUser

from ..errors import ServerError
import jwt
import datetime
import bson
import urllib
from aiohttp import ClientSession, web


class SignUpEndpoint(Endpoint):
    """
        Handle Initial account creation
    """

    name = "Sign Up"

    async def postProcess(
        self,
        email: str,
        username: str,
        password: str,
    ):

        user = await createUser(
            db=self.settings.db,
            username=username,
            email=email,
            password=password,
        )

        token = await setCurrentUser(
            self,
            self.settings.db,
            self.settings.jwtKey,
            user,
        )
        return {"success": "yes"}

    Post = newMethod(
        name="Sign Up",
        httpMethod="POST",
        description=
        "Create a new user with the given username, email, and password.",
        process=postProcess,
        bodyParameters={
            "email": EmailField(
                description="The email of the user being created"
            ),
            "username": UsernameField(
                description="The username of the user being created"
            ),
            "password": NonBlankStringField(
                description="The password to set for the new user"
            ),
        },
        responseFields={
            "success": Field(
                description="A boolean of whether the user was created"
            ),
            "errors": ListField(DictField({})),
        }
    )


class LogInEndpoint(Endpoint):
    """
    Log in a user
    """
    name = "Log In"

    async def postProcess(
        self,
        email: str,
        password: str,
    ):
        user = await authenticateUser(
            db=self.settings.db,
            email=email,
            password=password,
        )
        token = await setCurrentUser(
            self,
            self.settings.db,
            self.settings.jwtKey,
            user,
        )

        return {
            "token": token,
            "currentUser": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
            },
        }

    Post = newMethod(
        name="Log In",
        httpMethod="POST",
        description="Log in the use with the given email and password",
        process=postProcess,
        bodyParameters={
            "email": EmailField(),
            "password": StringField(),
        },
        responseFields={
            "token": StringField(),
            "currentUser": DictField({
                "id": StringField(),
                "username": StringField(),
                "email": EmailField(),
            }),
            "errors": ListField(DictField({})),
        }
    )


class LogOutEndpoint(Endpoint):
    """
    Log out the Current User
    """

    name = "Log Out"

    async def process(self, ):
        self.unsetCookie("authentication", )
        self.unsetCookie("currentUser", )
        return {}

    Get = newMethod(
        name="Log Out",
        httpMethod="GET",
        description=
        "Log out the current user by unsetting the relevant cookies",
        process=process,
        responseFields={
            "errors": ListField(DictField({})),
        }
    )


class MeEndpoint(Endpoint):
    """
    Return information about the currently logged in user
    """

    name = "Me"

    async def processGet(self, currentUser):
        await setCurrentUser(
            self,
            self.settings.db,
            self.settings.jwtKey,
            currentUser,
        )
        return {
            "currentUser": {
                "id": str(currentUser["_id"]),
                "username": currentUser["username"],
                "email": currentUser["email"],
            },
        }

    Get = newMethod(
        name="Get Current User",
        httpMethod="GET",
        description="Return information about the currently logged in user",
        process=processGet,
        responseFields={
            "currentUser": DictField({
                "id": StringField(),
                "username": StringField(),
                "email": EmailField(),
            }),
            "errors": ListField(DictField({})),
        }
    )


def generateOAuthEndpoint(
    clientID: str,
    clientSecret: str,
    redirectUri: str,
    responseType: str,
    grantType: str,
    scope: str,
    authorizationUri: str,
    tokenUri: str,
    handleTokenResponse=None,
):
    async def process(
        self,
        code=None,
        state=None,
    ):
        if code == None:
            raise web.HTTPFound(
                location=authorizationUri + "?" + urllib.parse.urlencode({
                    "response_type": responseType,
                    "client_id": clientID,
                    "redirect_uri": redirectUri,
                    "scope": scope,
                })
            )

        async with ClientSession() as session:
            async with session.get(
                tokenUri,
                params={
                    "code": code,
                    "grant_type": grantType,
                    "redirect_uri": redirectUri,
                    "client_id": clientID,
                    "client_secret": clientSecret,
                }
            ) as response:
                token = await response.json()
                if handleTokenResponse:
                    await handleTokenResponse(
                        handler=self,
                        token=token,
                    )

    class OAuthEndpoint(Endpoint):
        Get = newMethod(
            name="Oauth Login",
            httpMethod="GET",
            description="OAuth 2.0 login endpoint",
            process=process,
            queryParameters={
                "code": StringField(optional=True),
                "state": StringField(optional=True),
            }
        )

    return OAuthEndpoint
