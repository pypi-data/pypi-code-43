import unittest
import faker

from aiohttp.test_utils import unittest_run_loop

from ..test_case import AuthenticatedClericusTestCase

fake = faker.Faker()


class SignUpTestCase(AuthenticatedClericusTestCase):
    @unittest_run_loop
    async def testSignup(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

    @unittest_run_loop
    async def testInvalidUsername(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": "",
            "email": fake.email(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        user["username"] = 4
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        user["username"] = "moo cow"
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

    @unittest_run_loop
    async def testInvalidEmail(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.user_name(),
            "email": "moo",
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        user["email"] = 5
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

    @unittest_run_loop
    async def testDuplicateUsernameSignup(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.user_name().lower(),
            "email": fake.email(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

        user["email"] = fake.email()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test case insensitive matching
        user["username"] = user["username"].upper()
        user["email"] = fake.email()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test with space
        user["username"] = "  " + user["username"] + "  "
        user["email"] = fake.email()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

    @unittest_run_loop
    async def testDuplicateEmailSignup(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.user_name(),
            "email": fake.email().lower(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

        user["username"] = fake.user_name()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test case insensitive matching
        user["email"] = user["email"].upper()
        user["username"] = fake.user_name()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test with space
        user["email"] = "    " + user["email"] + "   "
        user["username"] = fake.user_name()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)


if __name__ == '__main__':
    unittest.main()