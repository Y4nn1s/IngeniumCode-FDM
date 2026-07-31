# Migración manual - Fase 3 Filiacion
# La BD real tiene 'posicion' y 'lateralidad' como VARCHAR (choices de texto).
# La 0001_initial del repo describe un estado más nuevo que la BD.
# Esta migración agrega las columnas FK correctas de forma segura:
# - posicion_id → core_catposicion
# - lateralidad_id → core_catlateralidad
# Y además añade las columnas faltantes y corrige el on_delete de usuario.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_poblar_catalogos'),
        ('filiacion', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # --- 1. Agregar columna numero_acta_nacimiento si no existe ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS numero_acta_nacimiento VARCHAR(50) NOT NULL DEFAULT '';
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta
                DROP COLUMN IF EXISTS numero_acta_nacimiento;
            """
        ),

        # --- 2. Agregar columna es_condicion_especial si no existe ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS es_condicion_especial BOOLEAN NOT NULL DEFAULT FALSE;
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta
                DROP COLUMN IF EXISTS es_condicion_especial;
            """
        ),

        # --- 3. Agregar columna observacion_medica si no existe ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS observacion_medica TEXT;
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta
                DROP COLUMN IF EXISTS observacion_medica;
            """
        ),

        # --- 4. Agregar columna cedula_identidad si no existe ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS cedula_identidad VARCHAR(15);
                CREATE UNIQUE INDEX IF NOT EXISTS filiacion_atleta_cedula_uniq
                    ON filiacion_atleta (cedula_identidad)
                    WHERE cedula_identidad IS NOT NULL;
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS filiacion_atleta_cedula_uniq;
                ALTER TABLE filiacion_atleta DROP COLUMN IF EXISTS cedula_identidad;
            """
        ),

        # --- 5. Agregar columna becado si no existe ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS becado BOOLEAN NOT NULL DEFAULT FALSE;
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta DROP COLUMN IF EXISTS becado;
            """
        ),

        # --- 6. Agregar columna foto_perfil si no existe ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(255);
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta DROP COLUMN IF EXISTS foto_perfil;
            """
        ),

        # --- 7. Agregar FK posicion_id → core_catposicion (nueva columna) ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS posicion_id INTEGER
                    REFERENCES core_catposicion(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta DROP COLUMN IF EXISTS posicion_id;
            """
        ),

        # --- 8. Agregar FK lateralidad_id → core_catlateralidad (nueva columna) ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE filiacion_atleta
                ADD COLUMN IF NOT EXISTS lateralidad_id INTEGER
                    REFERENCES core_catlateralidad(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE filiacion_atleta DROP COLUMN IF EXISTS lateralidad_id;
            """
        ),

        # --- 9. Corregir on_delete de Representante.usuario: CASCADE → SET NULL ---
        migrations.AlterField(
            model_name='representante',
            name='usuario',
            field=models.OneToOneField(
                blank=True,
                help_text='Cuenta de usuario asociada al representante',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='representante',
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        # --- 10. Registrar en el ORM de Django los nuevos campos FK ---
        # Django necesita conocer estos campos en su estado interno.
        # Usamos SeparateDatabaseAndState para que no vuelva a tocar la BD
        # (ya lo hicimos con RunSQL arriba), pero sí actualice el estado del ORM.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='atleta',
                    name='posicion',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='atletas',
                        to='core.catposicion',
                    ),
                ),
                migrations.AlterField(
                    model_name='atleta',
                    name='lateralidad',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='atletas',
                        to='core.catlateralidad',
                    ),
                ),
                migrations.AlterField(
                    model_name='atleta',
                    name='observacion_medica',
                    field=models.TextField(blank=True, null=True),
                ),
            ],
            database_operations=[],  # Ya se aplicó via RunSQL, no repetir.
        ),
    ]
