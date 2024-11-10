from .client import IAClient

class ClientManager:
    _clientsInit = {}

    def __init__(self):
        self._clients = []
    
    @staticmethod
    def initWithConfig(config:dict):
        clientManager = ClientManager()
        for clientConfig in config:
            clientName = clientConfig['name']
            del clientConfig['name']
            clientManager._clients.append(ClientManager._clientsInit[clientName](clientConfig))
        return clientManager
    @staticmethod
    def registerClient(name:str,client):
        ClientManager._clientsInit[name] = (lambda config: client(**config)) if issubclass(client, IAClient) else client

    def analyze(self,comments:list):
        for client in self._clients:
            client.analyze(comments)
    