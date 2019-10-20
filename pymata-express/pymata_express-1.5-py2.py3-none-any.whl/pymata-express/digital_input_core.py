import asyncio
import sys
from pymata_express import PymataExpress


def my_callback(data):
    print(data)


async def digital_in(my_board, pin):
    await my_board.set_pin_mode(pin, Constants.INPUT, callback=my_callback)

    while True:
        value = await my_board.digital_read(pin)
        # print(value)
        await asyncio.sleep(.5)

loop = asyncio.get_event_loop()
board = PymataExpress()
try:
    loop.run_until_complete(digital_in(board, 13))
except KeyboardInterrupt:
    sys.exit(0)
