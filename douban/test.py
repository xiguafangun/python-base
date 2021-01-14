# import httpx
# import asyncio


# async def main():
#     async with httpx.AsyncClient() as client:
#         response = await client.get('https://www.example.com/')
#         print(response)


# asyncio.run(main())


class Manager:
    # _instance_lock = threading.Lock()
    abc = False

    def __new__(cls, *args, **kwargs):
        return '213123'
        if not hasattr(cls, '_instance'):
            # with cls._instance_lock:
            if not hasattr(cls, '_instance'):
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        print(self.abc)
        self.abc = True
        print('wfwefwef')


Manager()
Manager()
Manager()
Manager()