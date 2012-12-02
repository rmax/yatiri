from yatiri import web
from twisted.application import service, internet


yatiri = web.get_app()
application = service.Application("yatiri")

internet.TCPServer(8888, yatiri).setServiceParent(application)


