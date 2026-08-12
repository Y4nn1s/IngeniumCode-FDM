from django.db import models


class CatCargo(models.Model):
    """Catálogo de cargos del personal de la academia."""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

    def __str__(self):
        return self.nombre


class CatLicencia(models.Model):
    """Catálogo de tipos de licencia deportiva/profesional."""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"

    def __str__(self):
        return self.nombre


class CatGenero(models.Model):
    """Catálogo de géneros."""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"

    def __str__(self):
        return self.nombre


class CatPosicion(models.Model):
    """Catálogo de posiciones de juego."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Posición"
        verbose_name_plural = "Posiciones"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CatLateralidad(models.Model):
    """Catálogo de lateralidad del jugador (diestro, zurdo, ambidiestro)."""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Lateralidad"
        verbose_name_plural = "Lateralidades"

    def __str__(self):
        return self.nombre


class CatTipoPartido(models.Model):
    """Catálogo de tipos de partido."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tipo de Partido"
        verbose_name_plural = "Tipos de Partido"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CatCondicionPartido(models.Model):
    """Catálogo de condición del partido (local, visitante, neutral)."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Condición de Partido"
        verbose_name_plural = "Condiciones de Partido"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CatBanco(models.Model):
    """Catálogo de bancos venezolanos según código SUDEBAN."""
    id = models.AutoField(primary_key=True)
    codigo_sudeban = models.CharField(max_length=10)
    nombre = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"

    def __str__(self):
        return f"{self.codigo_sudeban} - {self.nombre}"


class CatEstadoPago(models.Model):
    """Catálogo de estados de un pago."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField()

    class Meta:
        verbose_name = "Estado de Pago"
        verbose_name_plural = "Estados de Pago"

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class CatMetodoPago(models.Model):
    """Catálogo de métodos de pago aceptados."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CatEstadoPartido(models.Model):
    """Catálogo de estados de un partido (workflow deportivo)."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Estado de Partido"
        verbose_name_plural = "Estados de Partido"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CatTipoPatrocinante(models.Model):
    """Catálogo de tipos de ente patrocinante (empresa, persona natural, etc.)."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tipo de Patrocinante"
        verbose_name_plural = "Tipos de Patrocinante"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CatFuenteTasaBCV(models.Model):
    """Catálogo de fuentes de origen de la tasa BCV (DolarAPI, manual, seed)."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Fuente de Tasa BCV"
        verbose_name_plural = "Fuentes de Tasa BCV"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
