from aiohttp.web import middleware, HTTPError
import datetime
import bson
import jwt
from colors import green, red


def logger(usernameField="username"):
    @middleware
    async def logRequest(request, handler):
        start = datetime.datetime.utcnow()
        try:
            response = await handler(request)

            status = (
                red(response.status)
                if response.status >= 400 else green(response.status)
            )
            print(
                status,
                request.method,
                request.path,
                getattr(
                    request,
                    "currentUser",
                    {usernameField: "Unauthenticated"},
                )[usernameField],
                f"{int((datetime.datetime.utcnow() - start).total_seconds() * 1000)}ms",
            )

            return response
        except HTTPError as err:
            print(
                red(err.status),
                request.method,
                request.path,
                getattr(
                    request,
                    "currentUser",
                    {usernameField: "Unauthenticated"},
                )[usernameField],
                f"{int((datetime.datetime.utcnow() - start).total_seconds() * 1000)}ms",
            )

            raise err
        except Exception as err:
            print(type(err), err)
            raise err

    return logRequest


def allowCors(origins):
    @middleware
    async def middle(request, handler):
        resp = await handler(request)
        try:
            origin = request.headers.get('Origin')[0]
        except:
            origin = None
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        if origin in origins:
            resp.headers.add("Access-Control-Allow-Origin", origin)
        else:
            defaultOrigin = origins[0] if origins else "*"
            resp.headers.add("Access-Control-Allow-Origin", defaultOrigin)

        try:
            requestHeaders = request.headers.get(
                'Access-Control-Request-Headers'
            )
            if requestHeaders:
                resp.headers.add(
                    "Access-Control-Allow-Headers", requestHeaders
                )
        except:
            pass

        return resp

    return middle


@middleware
async def removeServerHeader(request, handler):
    response = await handler(request)
    response.headers["Server"] = ""
    return response


def authentication(
    db, secretKey, cookieName="authentication", headerKey="X-Auth-Token"
):
    @middleware
    async def middle(request, handler):
        try:
            value = request.cookies[cookieName]
        except:
            value = None

        if value is None and headerKey:
            value = request.headers.get(headerKey, None)

        if value:
            try:
                parsed = jwt.decode(
                    value,
                    secretKey,
                    algorithms=['HS256'],
                )
                request.currentUser = await db.user.find_one({
                    "_id": bson.ObjectId(parsed["id"]),
                })
            except:
                # TODO: Log this
                pass
        return await handler(request)

    return middle


async def setCurrentUser(
    method,
    db,
    secretKey,
    user,
    cookiename="authentication",
    expiration=datetime.timedelta(days=1)
):
    now = datetime.datetime.utcnow()
    token = jwt.encode(
        payload={
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "exp": now + expiration,
            "iat": now,
        },
        key=secretKey,
        algorithm='HS256',
    ).decode("utf-8")
    method.setCookie("authentication", token)
    return token