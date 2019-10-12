from aiohttp.web import middleware
import datetime
import bson
import jwt


def logger(usernameField="username"):
    @middleware
    async def logRequest(request, handler):
        start = datetime.datetime.utcnow()
        resp = await handler(request)
        print(
            resp.status,
            request.method,
            request.path,
            getattr(
                request,
                "currentUser",
                {usernameField: "Unauthenticated"},
            )[usernameField],
            f"{int((datetime.datetime.utcnow() - start).total_seconds() * 1000)}ms",
        )
        return resp


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


def authentication(db, secretKey, cookieName="authentication"):
    @middleware
    async def middle(request, handler):
        try:
            value = request.cookies[cookieName]
            parsed = jwt.decode(
                value,
                secretKey,
                algorithms=['HS256'],
            )
            request.currentUser = await db.user.find_one({
                "_id": bson.ObjectId(parsed["id"]),
            })
        except:
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