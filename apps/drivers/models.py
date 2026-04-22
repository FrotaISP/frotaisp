# apps/drivers/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel


class Driver(TimeStampedModel):
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.PROTECT,
        related_name='drivers',
        verbose_name='Empresa',
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        verbose_name='Usuario'
    )
    cnh = models.CharField('CNH', max_length=20)
    cnh_expiration = models.DateField('Validade da CNH')
    phone = models.CharField('Telefone', max_length=20)
    address = models.TextField('Endereco', blank=True)
    is_available = models.BooleanField('Disponivel', default=True)
    avatar = models.ImageField('Foto', upload_to='drivers/', blank=True, null=True)

    class Meta:
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'
        ordering = ['user__first_name', 'user__last_name']
        constraints = [
            models.UniqueConstraint(fields=['company', 'cnh'], name='unique_driver_cnh_per_company'),
        ]

    def save(self, *args, **kwargs):
        if not self.company_id:
            try:
                self.company = self.user.profile.company
            except Exception:
                from apps.accounts.models import Company
                self.company = Company.get_default_company()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
