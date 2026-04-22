from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Criacao'),
        ('update', 'Atualizacao'),
        ('delete', 'Exclusao'),
        ('login', 'Login'),
        ('other', 'Outro'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.SET_NULL, related_name='audit_logs', null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, related_name='audit_logs', null=True, blank=True)
    action = models.CharField('Acao', max_length=20, choices=ACTION_CHOICES, default='other')
    path = models.CharField('Caminho', max_length=255)
    method = models.CharField('Metodo', max_length=10)
    status_code = models.PositiveSmallIntegerField('Status HTTP', null=True, blank=True)
    object_repr = models.CharField('Objeto', max_length=255, blank=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.CharField('User agent', max_length=255, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Auditoria'
        verbose_name_plural = 'Registros de Auditoria'
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user_id else 'anonimo'
        return f'{self.get_action_display()} - {username} - {self.path}'
