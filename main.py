from aiohttp import web
from kiss import kiss_ax25
import asyncio

index_file = open("index.html")
index_html = index_file.read()
index_file.close()

ax25_iface = kiss_ax25("KN4VHM")

async def get_message(request):
	global ax25_iface
	call, message = ax25_iface.recv()
	data = json.dumps({"callsign":call,"message":message})
	return web.Response(text=data,content_type='application/json')

async def index_handle(request):
	global index_html
	return web.Response(text=index_html,content_type='text/html')

async def send_message(request):
	message = await request.read()
	print(message.decode("ascii"))
	global ax25_iface
	ax25_iface.send('IDENT',message.decode("ascii"))
	data = json.dumps({"callsign":ax25_iface.callsign,"message":message.decode("ascii")})
	return web.Response(text=data)

app = web.Application()
app.router.add_get('/', index_handle)
app.router.add_get('/recv', get_message)
app.router.add_post('/send', send_message)
web.run_app(app)