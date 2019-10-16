# demo.py
import asyncio, time

# asyncio.wait() 等待执行完成
async def foo():
    await asyncio.sleep(2)
    print("done")
    return 50


async def main():
    task = asyncio.create_task(foo())
    # 执行其他任务
    print('看看会不会提前出现...')
    await asyncio.wait({task}) # 启动协程 并创建一个等待对象

asyncio.run(main())