from django.db import models

# --- Modelos ---

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=200)
    rif = models.CharField(max_length=20, unique=True)
    rubro = models.CharField(max_length=100)
    telefono_contacto = models.CharField(max_length=20)

    def __str__(self):
        return self.razon_social

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, related_name='compras')
    fecha_compra = models.DateField()
    descripcion_insumo = models.TextField()
    cantidad = models.PositiveIntegerField()
    costo_total_usd = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Compra a {self.proveedor} ({self.fecha_compra})"