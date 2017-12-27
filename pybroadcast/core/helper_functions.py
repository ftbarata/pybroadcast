import paho.mqtt.client as mqtt
from .models import SendMessageHistory, OperationLog, UsuariosAutorizados
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from ldap3 import Server, Connection, ALL
from django.conf import settings
from django.contrib.auth import authenticate, login, logout


def _get_ldap_user_attrs_as_dict_of_lists(username, attr_list=['l'], like_sql_like = False):
    server = Server(settings.LDAP_SERVER, get_info=ALL)
    conn = Connection(server, auto_bind=True)
    if like_sql_like:
        conn.search(settings.LDAP_SEARCH_BASE, '(uid={})'.format('*' + username + '*'), attributes=attr_list)
        lista = []
        for i in conn.response:
            lista.append(i['attributes']['uid'][0])
        return lista
    else:
        conn.search(settings.LDAP_SEARCH_BASE, '(uid={})'.format(username), attributes=attr_list)
        for dict_item_list in conn.response:
            if 'attributes' in dict_item_list.keys():
                return dict_item_list['attributes']
    return None


def login_user(request):
    if not request.user.is_authenticated:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if _get_ldap_user_attrs_as_dict_of_lists(user) is not None:
                user_lotacao = _get_ldap_user_attrs_as_dict_of_lists(user, ['l'])['l'][0]
                nome_completo = _get_ldap_user_attrs_as_dict_of_lists(user, ['gecos'])['gecos']
                request.session['nome_completo'] = nome_completo
            else:
                user_lotacao = 'nogroup'
                request.session['nome_completo'] = '(Nome não encontrado)'
            request.session['lotacao'] = user_lotacao
            return True
        else:
            return False


def logout_user(request):
    logout(request)
    return True


def _sendHistory(usuario, ip, lotacao,titulo_mensagem,mensagem):
    SendMessageHistory.objects.create(usuario=usuario,ip=ip, lotacao=lotacao, titulo_mensagem=titulo_mensagem, conteudo_mensagem=mensagem)


def _getUserFromSessionId(request):
    session_id = request.session.session_key
    session = Session.objects.get(session_key=session_id)
    uid = session.get_decoded().get('_auth_user_id')
    user_from_session_id = User.objects.get(pk=uid)
    fullname = User.objects.get(username=user_from_session_id).get_short_name()
    return {'username': user_from_session_id, 'fullname':fullname}


def _insertOpLog(usuario, ip,lotacao,descricao):
    OperationLog.objects.create(usuario=usuario, ip=ip, lotacao=lotacao, descricao=descricao)

def _getUFbyLotacao(lotacao):
    return lotacao[0:2].lower()


def _publish(username, message, hostname=settings.BROKER_SERVER):
    topic = _getTopicFromSender(username)
    if topic:
        client = mqtt.Client()
        client.disable_logger()
        client.username_pw_set('pybroadcast', '!#@-pybroadcast')
        client.connect(hostname, 1883, 60)
        client.publish(topic=topic.lower(), payload=message)
        print('Publicando em {}'.format(topic.lower()))
        client.disconnect()
        return True
    else:
        return False


def _getTopicFromSender(username):
    try:
        state = _get_ldap_user_attrs_as_dict_of_lists(username, ['st'])['st'][0]
    except TypeError:
        state = None
    if state is not None:
        description = _get_ldap_user_attrs_as_dict_of_lists(username, ['description'])['description'][0]
        lotacao = _get_ldap_user_attrs_as_dict_of_lists(username, ['l'])['l'][0]
        if 'UA' in str(description).upper()[0:3]:
            if 'BRASILIA' in str(description).upper() and 'BSB' in str(lotacao).upper():
                return 'ua/brasilia'
            else:
                return 'ua/{}'.format(state)
        elif 'DF-SUREG-E-ENTORNO' in str(lotacao).upper():
            return 'sureg/df'
        elif 'DF-SUREG-E-ENTORNO' not in str(lotacao).upper() and state.lower() == 'df':
            return 'df/matriz'
        else:
            return 'sureg/{}'.format(state)
    else:
        return None


def _addAuthorizedUser(username, adicionado_por, ip, lotacao_username):
    if UsuariosAutorizados.objects.filter(usuario=username).exists():
        return 'jaexiste'
    else:
        try:
            lotacao = _get_ldap_user_attrs_as_dict_of_lists(username, ['l'])['l'][0]
            UsuariosAutorizados.objects.create(usuario=username, lotacao=lotacao, adicionado_por=adicionado_por)
            _insertOpLog(usuario=adicionado_por,ip=ip, lotacao=lotacao_username,descricao='Adicionou {} aos usuários autorizados.'.format(str(username).upper()))
            return 'ok'
        except TypeError:
            return 'naoexistenoldap'



def _deleteAuthorizedUser(removido_por, ip, lotacao_username, id):
    if UsuariosAutorizados.objects.filter(pk=id).exists():
        username = UsuariosAutorizados.objects.get(pk=id)
        UsuariosAutorizados.objects.filter(pk=id).delete()
        _insertOpLog(usuario=removido_por, ip=ip, lotacao=lotacao_username,descricao='Removeu {} dos usuários autorizados.'.format(str(username).upper()))
        return True
    else:
        return False