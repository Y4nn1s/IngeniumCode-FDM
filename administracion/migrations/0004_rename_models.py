# Migración Fase 5: Limpieza y renombramiento definitivo en administracion.
# Operaciones:
#   1. Eliminar tablas legadas vía RunSQL (nombres reales en PostgreSQL).
#   2. Sincronizar estado del ORM con SeparateDatabaseAndState.
#   3. Renombrar Personal2 → Personal, Categoria2 → Categoria,
#      CategoriaEntrenadores2 → CategoriaEntrenadores.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0003_migrar_personal'),
        ('filiacion', '0002_alter_atleta_lateralidad_and_more'),
        ('deportivo', '0002_partido_condicion_legacy_partido_tipo_legacy_and_more'),
        ('finanzas', '0002_pago_banco_emisor_legacy_pago_estado_legacy_and_more'),
    ]

    operations = [
        # === Paso 1: Eliminar tablas legadas (por nombre real en BD) ===
        migrations.RunSQL(
            sql="""
                DROP TABLE IF EXISTS administracion_entrenador CASCADE;
                DROP TABLE IF EXISTS administracion_delegado CASCADE;
                DROP TABLE IF EXISTS administracion_coordinador CASCADE;
                DROP TABLE IF EXISTS administracion_categoria_entrenadores_asignados CASCADE;
                DROP TABLE IF EXISTS administracion_categoria CASCADE;
                DROP TABLE IF EXISTS administracion_personal CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # === Paso 2: Informar al ORM que los modelos legados ya no existen ===
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='CategoriaEntrenadores'),
                migrations.DeleteModel(name='Personal'),
            ],
            database_operations=[],  # Ya ejecutado vía RunSQL
        ),

        # === Paso 3: Renombrar modelos v2 a sus nombres definitivos ===
        # Django traduce RenameModel a ALTER TABLE en PostgreSQL.
        migrations.RenameModel(
            old_name='Personal2',
            new_name='Personal',
        ),
        migrations.RenameModel(
            old_name='Categoria2',
            new_name='Categoria',
        ),
        migrations.RenameModel(
            old_name='CategoriaEntrenadores2',
            new_name='CategoriaEntrenadores',
        ),
    ]
