from yatiri import search
from twisted.application import service, internet


yatiri = search.get_app()
application = service.Application("yatiri")

internet.TCPServer(9999, yatiri).setServiceParent(application)


