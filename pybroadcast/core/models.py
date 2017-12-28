from django.db import models


class SendMessageHistory(models.Model):
    usuario = models.CharField(max_length=80, verbose_name='Usuário')
    ip = models.CharField(max_length=20, verbose_name='IP')
    lotacao = models.CharField(max_length=15, verbose_name='Lotação')
    estado_lotacao = models.CharField(max_length=2, verbose_name='Estado da Lotação')
    timestamp = models.DateTimeField(verbose_name='Data e Hora', auto_now_add=True)
    titulo_mensagem = models.CharField(max_length=30, verbose_name='Título da Mensagem')
    conteudo_mensagem = models.CharField(max_length=210, verbose_name='Mensagem')

    class Meta:
        verbose_name = 'Histórico de Mensagens'
        verbose_name_plural = 'Históricos de Mensagens'
        permissions = (
            ("send_message", "Pode enviar mensagens"),
        )

    def __str__(self):
        return str(self.usuario) + ' ' + str(self.timestamp)


class OperationLog(models.Model):
    usuario = models.CharField(max_length=80, verbose_name='Usuário')
    ip = models.CharField(max_length=20, verbose_name='IP')
    lotacao = models.CharField(max_length=15, verbose_name='Lotação')
    estado_lotacao = models.CharField(max_length=2, verbose_name='Estado da Lotação')
    timestamp = models.DateTimeField(verbose_name='Data e Hora', auto_now_add=True)
    descricao = models.CharField(max_length=30, verbose_name='Descrição')

    class Meta:
        verbose_name = 'Log de operação'
        verbose_name_plural = 'Logs de operações'

    def __str__(self):
        return str(self.usuario) + '(' + str(self.lotacao) + ')'


class UsuariosAutorizados(models.Model):
    usuario = models.CharField(max_length=80, verbose_name='Usuário')
    lotacao = models.CharField(max_length=15, verbose_name='Lotação')
    estado_lotacao = models.CharField(max_length=2, verbose_name='Estado da Lotação')
    adicionado_por = models.CharField(max_length=15, verbose_name='Adicionado por')
    timestamp = models.DateTimeField(verbose_name='Data e Hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Usuário autorizado'
        verbose_name_plural = 'Usuários autorizados'
        permissions = (
            ("edit_authorized", "Pode adicionar/remover usuários autorizados"),

        )

    def __str__(self):
        return str(self.usuario)
