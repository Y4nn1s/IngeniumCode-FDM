from django.contrib import admin

from core.models import (
    CatCargo, CatLicencia, CatGenero,
    CatPosicion, CatLateralidad,
    CatTipoPartido, CatCondicionPartido,
    CatBanco, CatEstadoPago, CatMetodoPago,
    CatEstadoPartido, CatTipoPatrocinante, CatFuenteTasaBCV,
)


@admin.register(CatCargo)
class CatCargoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(CatLicencia)
class CatLicenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(CatGenero)
class CatGeneroAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(CatPosicion)
class CatPosicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(CatLateralidad)
class CatLateralidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(CatTipoPartido)
class CatTipoPartidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(CatCondicionPartido)
class CatCondicionPartidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(CatBanco)
class CatBancoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo_sudeban', 'nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo_sudeban', 'nombre')


@admin.register(CatEstadoPago)
class CatEstadoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion')
    search_fields = ('codigo',)


@admin.register(CatMetodoPago)
class CatMetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(CatEstadoPartido)
class CatEstadoPartidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(CatTipoPatrocinante)
class CatTipoPatrocinanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(CatFuenteTasaBCV)
class CatFuenteTasaBCVAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
