from aiohttp import web
from kiss import kiss_ax25
import asyncio

index_file = open("index.html")
index_html = index_file.read()
index_file.close()

ax25_iface = kiss_ax25("KN4VHM")

async def get_root(request):
	print("html returned")
	global index_html
	return web.Response(text=index_html,content_type='text/html')

async def get_message(request):
	#print("Get Method")
	global ax25_iface
	call, message = ax25_iface.recv()
	if call == "None":
		return web.Response(text='None')
	return web.Response(text=call+': '+message)

async def create_message(request):
	data = await request.read()
	print(data.decode("ascii"))
	global ax25_iface
	ax25_iface.send('IDENT',data.decode("ascii"))
	return web.Response(text=data.decode("utf-8"))

app = web.Application()
app.router.add_get('/', get_root)
app.router.add_get('/message', get_message)
app.router.add_post('/message', create_message)
web.run_app(app)
