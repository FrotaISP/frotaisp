# apps/accounts/management/commands/generate_alert_notifications.py
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import Company, Notificacao
from apps.maintenance.models import PreventiveMaintenancePlan, WorkOrder
from apps.vehicles.models import VehicleChecklist, VehicleDocument


class Command(BaseCommand):
    help = 'Gera notificacoes para documentos, preventivas, checklists e ordens de servico pendentes.'

    def handle(self, *args, **options):
        total = 0
        for company in Company.objects.filter(is_active=True):
            recipients = self._recipients(company)
            if not recipients:
                continue
            messages = self._company_messages(company)
            for message, level in messages:
                total += self._notify(recipients, message, level)
        self.stdout.write(self.style.SUCCESS(f'{total} notificacoes geradas.'))

    def _recipients(self, company):
        User = get_user_model()
        return User.objects.filter(
            is_active=True,
            profile__company=company,
            profile__role__in=['admin', 'manager', 'operator'],
        ).distinct()

    def _company_messages(self, company):
        today = timezone.localdate()
        messages = []

        documents = VehicleDocument.objects.filter(
            company=company,
            is_active=True,
            expiration_date__lte=today + timedelta(days=30),
        ).select_related('vehicle', 'driver', 'driver__user')
        for document in documents:
            target = document.vehicle or document.driver or company
            days = document.days_until_expiration
            if days < 0:
                messages.append((f'Documento vencido: {document.title} ({target}) venceu ha {abs(days)} dias.', 'erro'))
            else:
                messages.append((f'Documento a vencer: {document.title} ({target}) vence em {days} dias.', 'alerta'))

        plans = PreventiveMaintenancePlan.objects.filter(company=company, status='active').select_related('vehicle')
        for plan in plans:
            if plan.is_overdue:
                messages.append((f'Preventiva vencida: {plan.service_name} do veiculo {plan.vehicle.plate}.', 'erro'))
            elif plan.is_due_soon:
                messages.append((f'Preventiva proxima: {plan.service_name} do veiculo {plan.vehicle.plate}.', 'alerta'))

        checklists = VehicleChecklist.objects.filter(
            company=company,
            status__in=['attention', 'blocked'],
            inspected_at__date__gte=today - timedelta(days=7),
        ).select_related('vehicle')
        for checklist in checklists:
            messages.append((f'Checklist com pendencia: {checklist.vehicle.plate} esta como {checklist.get_status_display()}.', 'erro' if checklist.status == 'blocked' else 'alerta'))

        work_orders = WorkOrder.objects.filter(
            company=company,
            status__in=['open', 'scheduled', 'in_progress', 'waiting_parts'],
        ).filter(
            Q(scheduled_date__lt=today) | Q(priority__in=['high', 'critical'])
        ).select_related('vehicle')
        for order in work_orders:
            messages.append((f'Ordem de servico pendente: OS #{order.pk} - {order.title} ({order.vehicle.plate}).', 'erro' if order.priority == 'critical' else 'alerta'))

        return messages

    def _notify(self, recipients, message, level):
        created = 0
        for user in recipients:
            exists = Notificacao.objects.filter(usuario=user, mensagem=message, lida=False).exists()
            if exists:
                continue
            Notificacao.objects.create(usuario=user, mensagem=message, tipo=level)
            created += 1
        return created
