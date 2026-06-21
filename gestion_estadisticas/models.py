# ventas/models.py
from django.db import models
from django.db.models import Sum, Count, Avg
from django.utils import timezone

class FacturaManager(models.Manager):
    def total_ventas(self):
        return self.aggregate(total=Sum('subtotal'))['total'] or 0

    def ventas_por_mes(self):
        return self.values('fecha__month').annotate(total=Sum('subtotal')).order_by('fecha__month')

    def ticket_promedio(self):
        return self.aggregate(promedio=Avg('subtotal'))['promedio'] or 0

class Factura(models.Model):
    cliente = models.CharField(max_length=200)
    fecha = models.DateField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    objects = FacturaManager()  # 👈 conectamos el manager
