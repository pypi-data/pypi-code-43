import asyncio
import re

from aiohttp import ClientSession

BASE_URL = "https://www.kaist.ac.kr/_prog/fodlst/index.php?site_dvs_cd=kr&menu_dvs_cd=050303&dvs_cd=%s&site_dvs=mobile"
DVS_DS = [
    ("fclt", "카이마루"),
    ("west", "서맛골"),
    ("east1", "동맛골"),
    ("east2", "동맛골 교직원식당"),
    ("emp", "교수회관"),
    ("icc", "문지캠퍼스"),
    ("hawam", "화암기숙사"),
    ("seoul", "서울캠퍼스"),
]

TABLE = re.compile(
    r"<table.*?class=\"menuTb\".*?>.*?<tbody>(.*?)</tbody>.*?</table>",
    re.DOTALL)
MENU = re.compile(r"<td.*?>(.*?)</td>", re.DOTALL)


def format_menu(menu):
    menu = re.sub(r"<.*?>", "", menu)
    menu = menu.replace("&lt;", "<").replace("&gt;", ">")
    menu = menu.replace("&amp;", "&").replace("&quot;", "\"")
    menu = menu.replace("\\", "₩").replace("-운영없음-", "")
    menu = menu.replace("미운영", "")
    menu = "\n".join((line.strip() for line in menu.splitlines()))
    menu = re.sub(r"\n\n\n*", "\n\n", menu)
    return menu


async def fetch_ds(session, entry):
    url = BASE_URL % entry[0]
    async with session.get(url) as response:
        assert response.status == 200
        body = await response.text()
        menus = [format_menu(menu) for menu in MENU.findall(body)]
        if len(menus) != 3:
            return {
                "ds": entry[1],
                "url": url,
            }

        return {
            "ds": entry[1],
            "url": url,
            "breakfast": menus[0],
            "lunch": menus[1],
            "dinner": menus[2],
        }


async def future_get_foods():
    tasks = []
    async with ClientSession() as session:
        for entry in DVS_DS:
            task = asyncio.ensure_future(fetch_ds(session, entry))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses
    return []


def get_foods():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(future_get_foods())
    foods = loop.run_until_complete(future)
    return foods


if __name__ == "__main__":
    for food in get_foods():
        print(food["ds"])
        print(food["url"])
        print(food["breakfast"])
        print(food["lunch"])
        print(food["dinner"])
        print("\n\n\n")
