# apps/accounts/migrations/0002_add_driver_role.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin',    'Administrador'),
                    ('manager',  'Gestor'),
                    ('operator', 'Operador'),
                    ('driver',   'Motorista'),
                    ('viewer',   'Visualizador'),
                ],
                default='viewer',
                max_length=20,
                verbose_name='Papel'
            ),
        ),
    ]
