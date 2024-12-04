from django.db import models
from django.core.exceptions import ValidationError
from Compras.models import EntregaFruta

# Descripción del trabajador temporal

class TrabajadorProduccion(models.Model):
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, unique=True)

# Especificaciones del producto final

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    calibre = models.CharField(max_length=50)
    peso_minimo = models.DecimalField(max_digits=5, decimal_places=2)
    peso_maximo = models.DecimalField(max_digits=5, decimal_places=2)

# Dato de lo que se pagara por caja terminada dependiendo de su calibre.

class TarifaCalibre(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tarifa_por_caja = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vigencia = models.DateTimeField(auto_now=True)

# Datos finales de producción luego de procesar todo el cargamento

class ProcesamientoMateriaPrima(models.Model):
    entrada_compra = models.ForeignKey(EntregaFruta, on_delete=models.CASCADE)
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)
    peso_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    peso_procesado = models.DecimalField(max_digits=10, decimal_places=2)
    merma = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_merma = models.DecimalField(max_digits=5, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.porcentaje_merma = (self.merma / self.peso_entrada) * 100
        super().save(*args, **kwargs)

    def clean(self):
        if self.peso_procesado > self.peso_entrada:
            raise ValidationError("Peso procesado no puede superar peso de entrada")

# Calculo de lo que se le debe pagar al trabajador de acuerdo a su producción

class ProduccionTrabajador(models.Model):
    trabajador = models.ForeignKey(TrabajadorProduccion, on_delete=models.CASCADE)
    procesamiento = models.ForeignKey(ProcesamientoMateriaPrima, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha = models.DateField()
    numero_cajas = models.IntegerField()
    peso_total_cajas = models.DecimalField(max_digits=10, decimal_places=2)
    tarifa_por_caja = models.DecimalField(max_digits=10, decimal_places=2)
    total_pago = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_pago = self.numero_cajas * self.tarifa_por_caja
        super().save(*args, **kwargs)

    def clean(self):
        total_producido = ProduccionTrabajador.objects.filter(
            procesamiento=self.procesamiento
        ).aggregate(models.Sum('peso_total_cajas'))['peso_total_cajas__sum'] or 0
        
        if total_producido + self.peso_total_cajas > self.procesamiento.peso_entrada - self.procesamiento.merma:
            raise ValidationError("Producción supera el peso disponible")

# Resumen de producción semanal que servirá como liquidación de sueldo semanal

class ResumenProduccionSemanal(models.Model):
    trabajador = models.ForeignKey(TrabajadorProduccion, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    total_cajas = models.IntegerField()
    total_pago = models.DecimalField(max_digits=10, decimal_places=2)

