import asyncio
import logging

logger = logging.getLogger(__name__)


class Timer:

    # 延迟执行一次
    @classmethod
    def delay(cls, callback , delay):

        return cls(callback , delay , 5 ,  1)

    # 延迟启动后，持续运行
    @classmethod
    def interval(cls, callback , delay , interval):

        return cls(callback, delay, interval , 0 )


    def __init__(self, callback ,  delay ,interval=1 , times=0 ):

        self._callback = callback
        self._interval_ = interval
        self._delay = delay
        self._times = times

        self._filled_times = 0

        self._task = asyncio.ensure_future(self._job(delay))
        
        logger.info(f'interval:{interval} ,delay:{delay } , times:{times}')

    async def _loop(self):
        
        while True:

            if asyncio.iscoroutinefunction(self._callback):

                await self._callback()
            else:
                self._callback()

            self._filled_times += 1

            if self._times ==0 or self._filled_times < self._times:
                    
                await asyncio.sleep(self._interval_)

            else:
                break


    async def _job(self,delay):

        logger.debug('job start')

        if delay > 0:

            await asyncio.sleep(delay)

        try:
            await self._loop()

        except asyncio.CancelledError:
            logger.debug('job canceled')
            
        except Exception as e:
            logger.error(str(e))
            raise
            
        finally:
            logger.debug('job end')

    def cancel(self):

        logger.debug('cancel task')

        if not self._task.done():
            self._task.cancel()

    def refresh(self):

        logger.debug('refresh task')

        self._task.cancel()
        self._task = asyncio.ensure_future(self._job(self._delay))

