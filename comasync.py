import asyncio

server = None

async def cb(reader, writer):
    print ('connection is requested')
    data = await reader.read()
    message = data.decode()
    print (message)

async def start_server():

    global server
    server = await asyncio.start_server(cb, '', 65001)

    async with server:
        await server.serve_forever()

asyncio.run(start_server())
