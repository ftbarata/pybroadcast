from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.models import User, Permission
from .helper_functions import login_user, logout_user, _publish, _sendHistory, _getUserFromSessionId, _getTopicFromSender, _addAuthorizedUser, _deleteAuthorizedUser, _get_ldap_user_attrs_as_dict_of_lists
from .models import SendMessageHistory, OperationLog, UsuariosAutorizados
import os


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'core/login.html', )
    else:
        remote_addr = request.META['REMOTE_ADDR']
        try:
            nome_completo = request.session['nome_completo']
        except KeyError:
            nome_completo = request.user
        return render(request, 'core/home.html', {'nome_completo': nome_completo, 'remote_addr': remote_addr})


def login(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            if login_user(request):
                nome_completo = request.session['nome_completo']
                usuario = User.objects.get(username=request.user)
                send_message_perm = usuario.user_permissions.filter(codename='send_message').exists()
                edit_authorized_perm = usuario.user_permissions.filter(codename='edit_authorized').exists()
                remote_addr = request.META['REMOTE_ADDR']
                if send_message_perm and edit_authorized_perm:
                    return render(request, 'core/home.html', {'nome_completo': nome_completo, 'remote_addr': remote_addr})
                else:
                    return render(request, 'core/home.html',{'nome_completo': nome_completo, 'remote_addr': remote_addr, 'alert_message': 'Atenção, você não tem permissão para enviar mensagem e editar autorizados'})
            else:
                return render(request, 'core/login.html', {'alert_message': 'Login ou senha incorreta.'})
        else:
            return render(request, 'core/home.html')
    else:
        return render(request, 'core/login.html')


def logout(request):
    if logout_user(request):
        return render(request, 'core/login.html', {'status_message': 'Você foi deslogado.'})


def about(request):
    if request.user.is_authenticated:
        remote_addr = request.META['REMOTE_ADDR']
        nome_completo = request.session['nome_completo']
        return render(request, 'core/about.html', {'nome_completo': nome_completo, 'remote_addr': remote_addr})
    else:
        return render(request, 'core/about.html')


def sendMessage(request):
    if request.user.is_authenticated:
        remote_addr = request.META['REMOTE_ADDR']
        title = request.POST['title']
        target = request.POST['target']
        message = request.POST['body']
        if target == 'multicast':
            body = message + '[$$]' + request.POST['enderecos']
        else:
            body = message
        lotacao = request.session['lotacao']
        estado_lotacao = str(_get_ldap_user_attrs_as_dict_of_lists(username=request.user, attr_list=['st'])['st'][0]).upper()
        username = str(_getUserFromSessionId(request)['username'])
        nome_completo = request.session['nome_completo']
        topic = _getTopicFromSender(username=username, remote_addr=remote_addr)
        usuario = User.objects.get(username=request.user)
        send_message_perm = usuario.user_permissions.filter(codename='send_message').exists()

        if send_message_perm:

            if _publish(username=username,message='{}[$$]{}'.format(title, body), remote_addr=remote_addr):
                _sendHistory(usuario=username,ip=remote_addr, lotacao=lotacao, estado_lotacao=estado_lotacao, titulo_mensagem=title, mensagem=body)
                return render(request, 'core/home.html', {'status_message':'Mensagem Enviada. Tópico: {}'.format(topic),'nome_completo': nome_completo, 'remote_addr': remote_addr})
            else:
                return render(request, 'core/home.html', {'status_message': 'Erro de cruzamento de dados cadastrais. Por favor, verifique seus dados de lotação no RH.', 'nome_completo': nome_completo, 'remote_addr': remote_addr})
        else:
            return render(request, 'core/home.html',{'nome_completo': nome_completo, 'remote_addr': remote_addr, 'alert_message': 'Você não tem permissão para enviar mensagens.'})
    else:
        return render(request, 'core/login.html', {'alert_message': 'Acesso negado. Faça o login primeiro.'})


def historico(request):
    if request.user.is_authenticated:
        remote_addr = request.META['REMOTE_ADDR']
        lotacao = request.session['lotacao']
        estado_lotacao = str(_get_ldap_user_attrs_as_dict_of_lists(username=request.user, attr_list=['st'])['st'][0]).upper()
        nome_completo = request.session['nome_completo']
        history_queryset = SendMessageHistory.objects.all().filter(estado_lotacao__iexact=estado_lotacao).order_by('-timestamp')
        operation_queryset = OperationLog.objects.all().filter(lotacao=lotacao).order_by('-timestamp')

        return render(request, 'core/historico.html', {'history_queryset': history_queryset, 'nome_completo':nome_completo, 'lotacao': lotacao, 'operation_history': operation_queryset, 'remote_addr': remote_addr})
    else:
        return render(request, 'core/login.html', {'alert_message': 'Acesso negado. Faça o login primeiro.'})


def getReverseDns(request):
    remote_addr = request.META['REMOTE_ADDR']
    if len(remote_addr) <= 15:
        octets_list = remote_addr.split('.')
        prefix = ''
        position = 0
        for i in octets_list:
            if position < 2:
                prefix += i + '.'
                position += 1
        if octets_list[2] == '1' or octets_list[2] == '2':
            prefix += '0.'
        else:
            prefix += octets_list[2] + '.'
        final_ip = prefix + '8'
        reverse = os.popen('host -t txt {}'.format(final_ip)).read()
        if 'NXDOMAIN' not in reverse:
            reverse_ip_list = str(reverse).split(' ')
            reverse = str(reverse_ip_list[len(reverse_ip_list) - 1]).lower()
            return render(request, 'core/reversedns.html', {'result': reverse.replace('.conab.gov.br.', '')})
        else:
            return render(request, 'core/reversedns.html', {'result': 'df'})
    else:
        return render(request, 'core/reversedns.html', {'result': 'False'})


def teste(request,username):
    topic = _getTopicFromSender(username)
    if topic is not None:
        return render(request, 'core/teste.html', {'result':topic.lower()})
    return render(request, 'core/teste.html', {'result': 'Usuario nao encontrado ou com dados incompletos no ldap.'})


def configuracoes(request):
    if request.user.is_authenticated:
        estado_lotacao = str(_get_ldap_user_attrs_as_dict_of_lists(username=request.user, attr_list=['st'])['st'][0]).upper()
        usuarios_autorizados = UsuariosAutorizados.objects.all().filter(Q(estado_lotacao__iexact=estado_lotacao)|Q(adicionado_por__iexact=request.user)).order_by('-timestamp')
        lotacao = request.session['lotacao']
        remote_addr = request.META['REMOTE_ADDR']
        nome_completo = request.session['nome_completo']
        if request.method == 'GET':
            return render(request, 'core/configuracoes.html', {'remote_addr': remote_addr, 'nome_completo': nome_completo, 'usuarios_autorizados': usuarios_autorizados})
        else:
            if UsuariosAutorizados.objects.all().filter(usuario=request.POST['usuario']).exists():
                return render(request, 'core/configuracoes.html',{'usuarios_autorizados': usuarios_autorizados, 'remote_addr': remote_addr,'nome_completo': nome_completo,'alert_message': 'Usuário {} já possui autorização.'.format(request.POST['usuario'].upper())})

            usuario = request.POST['usuario']
            estado_lotacao_new_user = str(_get_ldap_user_attrs_as_dict_of_lists(username=usuario, attr_list=['st'])['st'][0]).upper()
            adicionado_por = request.user
            edit_authorized_perm = User.objects.get(username=adicionado_por).user_permissions.filter(codename='edit_authorized').exists()

            if not User.objects.all().filter(username=usuario).exists():
                return render(request, 'core/configuracoes.html',{'usuarios_autorizados': usuarios_autorizados, 'remote_addr': remote_addr,'nome_completo': nome_completo,'alert_message': 'Usuário {} deve fazer o primeiro acesso ao sistema para ser adicionado na lista de autorizados.'.format(usuario.upper())})

            edit_authorized_perm_new_user = Permission.objects.get(codename='edit_authorized')
            send_message_perm_new_user = Permission.objects.get(codename='send_message')
            if edit_authorized_perm:
                if _addAuthorizedUser(username=usuario,adicionado_por=adicionado_por, ip=remote_addr, lotacao_username=lotacao, estado_lotacao=estado_lotacao, estado_lotacao_new_user=estado_lotacao_new_user) == 'ok':
                    User.objects.get(username=usuario).user_permissions.add(edit_authorized_perm_new_user, send_message_perm_new_user)
                    return render(request, 'core/configuracoes.html', {'status_message': 'Usuário adicionado.', 'usuarios_autorizados': usuarios_autorizados, 'remote_addr': remote_addr, 'nome_completo': nome_completo})
                elif _addAuthorizedUser(username=usuario,adicionado_por=adicionado_por, ip=remote_addr, lotacao_username=lotacao, estado_lotacao_new_user=estado_lotacao_new_user) == 'jaexiste':
                    return render(request, 'core/configuracoes.html', {'status_message': 'Erro ao adicionar: Usuário já está autorizado.', 'usuarios_autorizados': usuarios_autorizados, 'remote_addr': remote_addr, 'nome_completo': nome_completo})
                elif _addAuthorizedUser(username=usuario, adicionado_por=adicionado_por, ip=remote_addr, lotacao_username=lotacao, estado_lotacao_new_user=estado_lotacao_new_user) == 'naoexistenoldap':
                    return render(request, 'core/configuracoes.html', {'status_message': 'Erro ao adicionar: Usuário não encontrado no Ldap.','usuarios_autorizados': usuarios_autorizados, 'remote_addr': remote_addr,'nome_completo': nome_completo})
            else:
                return render(request, 'core/configuracoes.html',{'usuarios_autorizados': usuarios_autorizados, 'remote_addr': remote_addr,'nome_completo': nome_completo, 'alert_message':'Você não tem permissão para editar autorizados.'})

    else:
        return render(request, 'core/login.html', {'alert_message': 'Acesso negado. Faça o login primeiro.'})


def deleteAuthorizedUser(request, id):
    if request.user.is_authenticated:
        estado_lotacao = str(_get_ldap_user_attrs_as_dict_of_lists(username=request.user, attr_list=['st'])['st'][0]).upper()
        usuarios_autorizados = UsuariosAutorizados.objects.all().filter(Q(estado_lotacao__iexact=estado_lotacao) | Q(adicionado_por__iexact=request.user)).order_by('-timestamp')
        remote_addr = request.META['REMOTE_ADDR']
        nome_completo = request.session['nome_completo']
        removido_por = request.user
        lotacao = request.session['lotacao']
        usuario = User.objects.get(username=request.user)
        edit_authorized_perm = usuario.user_permissions.filter(codename='edit_authorized').exists()

        if edit_authorized_perm:
            if _deleteAuthorizedUser(removido_por=removido_por,ip=remote_addr, lotacao_username=lotacao, id=id):
                return render(request, 'core/configuracoes.html',{'remote_addr': remote_addr, 'nome_completo': nome_completo,'usuarios_autorizados': usuarios_autorizados, 'status_message': 'Usuário removido.'})
            else:
                return render(request, 'core/configuracoes.html',{'remote_addr': remote_addr, 'nome_completo': nome_completo,'usuarios_autorizados': usuarios_autorizados, 'status_message': 'Erro ao remover usuário.'})
        else:
            return render(request, 'core/configuracoes.html',{'remote_addr': remote_addr, 'nome_completo': nome_completo,'usuarios_autorizados': usuarios_autorizados, 'status_message': 'Usuário removido.', 'alert_message':'Você não tem permissão para editar usuários autorizados.'})
    else:
        return render(request, 'core/login.html', {'alert_message': 'Acesso negado. Faça o login primeiro.'})


def ajaxRequestLdapUser(request, username):
    usernames = _get_ldap_user_attrs_as_dict_of_lists(username, ['uid'], like_sql_like=True)
    return render(request,'core/ajax.html', {'result': usernames})


def downloads(request):
    if request.user.is_authenticated:
        remote_addr = request.META['REMOTE_ADDR']
        nome_completo = request.session['nome_completo']
        return render(request, 'core/downloads.html', {'remote_addr': remote_addr,'nome_completo':nome_completo})
    else:
        return render(request, 'core/downloads.html')