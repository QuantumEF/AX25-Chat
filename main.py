from aiohttp import web
from kiss import kiss_ax25
import asyncio

async def get_message(request):
	print("Get Method")
	global ax25_iface
	call, message = await ax25_iface.recv()
	if call == "None":
		return web.Response(text='None')
	#call = 'NOCALL'
	#message = 'placeholder'
	#await asyncio.sleep(1)
	return web.Response(text=call+': '+message)

async def index_handle(request):
	#html = str(open('index.html', 'rb').read())
	print("html returned")
	#return web.Response(text=html,content_type='text/html')
	return web.FileResponse('index.html')

async def send_message(request):
	data = await request.read()
	print(data.decode("ascii"))
	global ax25_iface
	ax25_iface.send('NOCALL',data.decode("ascii"))
	return web.Response(text=data.decode("utf-8"))

app = web.Application()
app.add_routes([web.get('/', index_handle),
				web.get('/recv', get_message),
				web.post('/send', send_message)])

ax25_iface = kiss_ax25("KN4VHM")
web.run_app(app)