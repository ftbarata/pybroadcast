from django.contrib import admin
from .models import SendMessageHistory, OperationLog, UsuariosAutorizados

admin.site.register(SendMessageHistory)
admin.site.register(UsuariosAutorizados)
admin.site.register(OperationLog)
