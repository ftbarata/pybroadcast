import paho.mqtt.client as mqtt
import socket
import urllib.error
import urllib.request as request
import tkinter as tk
import tkinter.messagebox as tkMessageBox

URL_GET_REVERSE_DNS='http://*****/reversedns'
SERVER='10.1.0.127'
USERNAME='://*****'
PASSWORD='://*****'

# def getVmLinuxAddress():
#     hostname = socket.gethostname()
#     ip = socket.gethostbyname(hostname)
#     if len(ip) <= 15:
#         prefix = ''
#         dotcount = 0
#         for char in ip:
#             if dotcount < 3:
#                 if char == '.':
#                     dotcount += 1
#                 prefix += char
#         return prefix + '8'
#     else:
#         input("Mais de um endereço IP encontrado neste host. Corrija por favor, e execute novamente a aplicação.\nPressione Enter para sair.")


def getReverseAddress():
    try:
        result = request.urlopen('{}'.format(URL_GET_REVERSE_DNS.replace('//', '/').replace('http:/', 'http://'))).read().decode().replace(' ', '').replace('\n', '')
        return result
    except urllib.error.HTTPError as e:
        print('Erro ao acessar {}. Problema de comunicação com a aplicacao Django.\n\nExcecao: {}'.format('{}'.format(URL_GET_REVERSE_DNS.replace('//', '/').replace('http:/', 'http://')), e))
        return False
    except urllib.error.URLError as f:
        print('Erro ao acessar {}. Problema de comunicação com a aplicacao Django.\n\nExcecao: {}'.format('{}'.format(URL_GET_REVERSE_DNS.replace('//', '/').replace('http:/', 'http://')), f))
        return False
    except ConnectionRefusedError as g:
        print('Erro ao acessar {}. Problema de comunicação com a aplicacao Django.\n\nExcecao: {}'.format('{}'.format(URL_GET_REVERSE_DNS.replace('//', '/').replace('http:/', 'http://')), g))
        return False


def getSubChannel(name):
    if name:
        if 'sureg' in name.lower():
            return 'sureg/' + name[len(name)-2:]
        elif 'ua' in name.lower():
            return 'ua/' + name[2:]
        elif name.lower() == 'df':
            return 'df/matriz'
        elif name.lower() == 'false':
            print('DNS Reverso nao encontrado.')
            return False
    else:
        return False



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    print('Conectado no topico: {}'.format(channel.lower()))
    client.subscribe(channel.lower())


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if len(message.split('[$$]')) == 2:
        print('Mensagem com destino BROADCAST recebida: {}'.format(message))
        title = message.split('[$$]')[0]
        body = message.split('[$$]')[1]
        root = tk.Tk()
        root.withdraw()
        tkMessageBox.showwarning(title,body)
        print('Disparando evento tkMessageBox.showwarning')
    elif len(message.split('[$$]')) > 2:
        title = message.split('[$$]')[0]
        body = message.split('[$$]')[1]
        targets = message.split('[$$]')[2].replace(' ', '').split(',')
        print('Mensagem com destino MULTICAST({}) recebida: {}'.format(targets,message))
        hostname = socket.gethostname()
        localip = socket.gethostbyname(hostname)
        for i in targets:
            if i == localip:
                root = tk.Tk()
                root.withdraw()
                print('Disparando evento tkMessageBox.showwarning')
                tkMessageBox.showwarning(title, body)
                break

print('Iniciando...\nConectando em {}'.format(SERVER))

client = mqtt.Client()
client.disable_logger()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(SERVER, 1883, 60)
    reversename = getReverseAddress()
    channel = getSubChannel(reversename)
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    if channel is not False:
        client.loop_forever()
    else:
        client.disconnect()
except ConnectionRefusedError:
    print('Erro ao conectar ao Daemon do Mosquitto em {}'.format(SERVER))
except ConnectionError:
    print('Erro ao conectar ao Daemon do Mosquitto em {}'.format(SERVER))
except KeyboardInterrupt:
    print('CTRL+C pressionado.\nFinalizado.')
