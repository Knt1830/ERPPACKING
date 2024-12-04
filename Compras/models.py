from django.db import models

#Las categorías escritas son de prueba, no estaría mal agregar la posibilidad de crear nuevas categorías por parte del cliente.


class Proveedor(models.Model):
    TIPO_PROVEEDOR_CHOICES = [
        ('fruta', 'Proveedor de Frutas'),
        ('insumos', 'Proveedor de Insumos'),
        ('oficina', 'Proveedor de Oficina'),
        ('limpieza', 'Proveedor de Limpieza')
    ]

#Esta información de la ficha del proveedor es preliminar, podrá agregarse o quitar información si así lo requiere el cliente. Se considera obligatorio tanto el RUT (Cedula de identidad chilena) como el nombre


    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    tipo_proveedor = models.CharField(max_length=50, choices=TIPO_PROVEEDOR_CHOICES)
    producto = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_proveedor_display()}"

#Aquí se especifica lo producido por la carga del productor almacenando esta información en su ficha


class EntregaFruta(models.Model):
    proveedor = models.ForeignKey(Proveedor, 
        on_delete=models.CASCADE, 
        related_name='entregas_fruta',
        limit_choices_to={'tipo_proveedor': 'fruta'}
    )
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    calibre = models.CharField(max_length=50)
    cantidad_cajas = models.IntegerField()
    peso_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Entrega de {self.proveedor.nombre} - {self.fecha_entrega}"
