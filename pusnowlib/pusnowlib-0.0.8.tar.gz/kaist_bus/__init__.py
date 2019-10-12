import asyncio
import re
from collections import OrderedDict
from datetime import timedelta

from aiohttp import ClientSession
from bs4 import BeautifulSoup


class TimeTableBase:
    name = None
    time_table = None
    fetch_done = False

    def __init__(self):
        self.time_table = OrderedDict()

    def add_bus_stop(self, bus_stop):
        if bus_stop not in self.time_table:
            self.time_table[bus_stop] = []

    def add_bus_time(self, bus_stop, bus_time):
        self.time_table[bus_stop].append(bus_time)

    def print_table(self):
        for stop in self.time_table:
            print(stop, "\t".join([str(td) for td in self.time_table[stop]]))

    async def get_data(self):
        raise NotImplementedError

    async def parse_table(self):
        raise NotImplementedError

    async def get_result(self):
        if not self.fetch_done:
            await self.get_data()
            await self.parse_table()
        result = {
            "name": str(self.name),
            "stops": [],
        }
        for bus_stop in self.time_table:
            stop = {"name": bus_stop, "times": self.time_table[bus_stop]}
            result["stops"].append(stop)

        return result


class MunJiTimeTable(TimeTableBase):
    name = "캠퍼스간"
    URL = "https://www.kaist.ac.kr/_prog/_board/?code=shuttle2&site_dvs_cd=kr&menu_dvs_cd=01070902"
    table_num = 0
    head_re = re.compile(r'(출발|도착|앞)$')
    non_stop = set(["No", "배차간격", "비고"])
    time_re = re.compile(r'([0-9]+)\:([0-9][0-9])')
    data = None

    async def get_data(self):
        async with ClientSession() as session:
            async with session.get(self.URL) as response:
                assert response.status == 200
                self.data = await response.text()

    async def parse_table(self):
        html = self.data
        soup = BeautifulSoup(html, features="html.parser")
        table = soup.find_all(class_="table1")[self.table_num]

        thead = table.thead
        tbody = table.tbody

        heads = []
        colspans = []
        for head in thead.tr.find_all("th"):
            htext = self.head_re.sub("", head.text.strip()).strip()
            htext = re.sub(r"\s", "", htext)

            if htext in self.non_stop:
                continue

            colspan = 1
            if "colspan" in head.attrs:
                colspan = int(head.attrs["colspan"])

            heads.append(htext)
            colspans.append(colspan)

        stops = [
            "%s→%s" % (start, end) for start, end in zip(heads, heads[1:])
        ]
        for stop in stops:
            self.add_bus_stop(stop)

        for tr in tbody.find_all("tr"):
            tds = iter(tr.find_all("td"))

            for stop, colspan in zip(stops, colspans):
                td = next(tds)
                td_colspan = 1
                if "colspan" in td.attrs:
                    td_colspan = int(td.attrs["colspan"])

                for _ in range(colspan - td_colspan):
                    td = next(tds)

                time_text = td.text

                time_data = self.time_re.search(time_text)

                if not time_data:
                    continue

                hour = int(time_data.group(1))
                minute = int(time_data.group(2))
                if hour < 5:
                    hour += 24

                ti = timedelta(hours=hour, minutes=minute)
                self.add_bus_time(stop, ti)
        self.fetch_done = True


class MunJiWeekendTimeTable(MunJiTimeTable):
    name = "캠퍼스간 주말"
    table_num = 1


class WolPyeongTimeTable(TimeTableBase):
    name = "월평/본교"


class OLEVTimeTable(TimeTableBase):
    name = "OLEV"


async def future_get_time_tables():
    tasks = []
    for time_table_t in [
            MunJiTimeTable,
            MunJiWeekendTimeTable,
    ]:
        time_table = time_table_t()
        task = asyncio.ensure_future(time_table.get_result())
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses


def get_time_tables():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(future_get_time_tables())
    time_tables = loop.run_until_complete(future)
    return time_tables


if __name__ == "__main__":
    import pprint
    pprint.pprint(get_time_tables())
