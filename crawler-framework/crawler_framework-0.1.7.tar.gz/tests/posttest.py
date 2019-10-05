import asyncio
from core_framework.crawlers import CrawlerBase

link = 'https://api.ipify.org'


class MyPost(CrawlerBase):
    def __init__(self, webpage, proxy_type):
        CrawlerBase.__init__(self, webpage, proxy_type=proxy_type)

    def start(self):
        future = asyncio.Task(self.gather(1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
        gathered_data = future.result()

    async def gather(self, step_id):
        futures, results = list(), list()
        semaphore = asyncio.Semaphore(20)
        futures.append(self.get_data(link, semaphore, step_id=1))

        for future in asyncio.as_completed(futures):
            try:
                results.append((await future))
            except Exception as e:
                print("gather error", str(e))
        return results

    async def get_data(self, link, semaphore, step_id):
        proc_id = 1
        async with semaphore:
            # prepare new request for this thread/process and return proxy sha

            # sha = self.async_new_request(proc_id=proc_id, protocols=['http'], new=True)
            sha = self.async_new_request(proc_id=proc_id, new=True)

            try:
                # acquire request and set request type on 2 (number 2 is GET request with proxy)

                r = self.requests.get(proc_id)
                r.request_type = 2
                await r.go('http://vikingwarrior.pythonanywhere.com/woc/login')
                # await r.go('http://crodesigner.pythonanywhere.com/')

                html = r.response.content
                html_raw = r.response.content_raw
                print(html)
                # print(html_raw)

                print(html)
                csrfmiddlewaretoken = html.find('input', {'name': 'csrfmiddlewaretoken'})['value']
                print(csrfmiddlewaretoken)

                r.request_type = 4
                r.payload = {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'username': 'draganm', 'password': 'Valkery123!'}

                await r.go('http://vikingwarrior.pythonanywhere.com/woc/login/')
                # await r.go('http://crodesigner.pythonanywhere.com/')
                html = r.response.content
                html_raw = r.response.content_raw
                print(html_raw)

            except Exception as e:
                import sys, os
                print("posttest.py get_data error", str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                e = '======================================\n ERRORS: \n +error type: %s \n +py location: %s \n +error line: %s \n +error description: %s "\n"  \n======================================' % (
                str(exc_type), os.path.abspath(fname), exc_tb.tb_lineno, str(e))
                print(e)
            finally:
                await r.async_ses.close()
                r.clean()
                # release proxy back in use if it is not released it will be not be available for that web_base next 30min
                self.release_proxy(sha)


if __name__ == '__main__':
    api = MyPost('ipify', proxy_type=1)
    api.start()
