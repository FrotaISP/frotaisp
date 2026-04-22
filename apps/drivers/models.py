# apps/drivers/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel

class Driver(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        verbose_name='Usuário'
    )
    cnh = models.CharField('CNH', max_length=20, unique=True)
    cnh_expiration = models.DateField('Validade da CNH')
    phone = models.CharField('Telefone', max_length=20)
    address = models.TextField('Endereço', blank=True)
    is_available = models.BooleanField('Disponível', default=True)
    avatar = models.ImageField('Foto', upload_to='drivers/', blank=True, null=True)

    class Meta:
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username