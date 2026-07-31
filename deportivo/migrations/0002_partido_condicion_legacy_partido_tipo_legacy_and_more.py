# Migración manual - Fase 4 App: deportivo
# La BD real tiene tipo y condicion como VARCHAR (choices de texto),
# y resultado como campo VARCHAR real (no era @property).
# Esta migración:
# 1. Renombra tipo/condicion a tipo_legacy/condicion_legacy (VARCHAR → VARCHAR)
# 2. Agrega nuevas FK tipo_id y condicion_id hacia core (nullable)
# 3. Elimina resultado de la BD (viola 3NF, se calcula desde goles)
# Usamos RunSQL + SeparateDatabaseAndState para no chocar con el ORM.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_poblar_catalogos'),
        ('deportivo', '0001_initial'),
    ]

    operations = [
        # --- 1. Renombrar tipo → tipo_legacy (VARCHAR → VARCHAR, sin tocar datos) ---
        migrations.RunSQL(
            sql="ALTER TABLE deportivo_partido RENAME COLUMN tipo TO tipo_legacy;",
            reverse_sql="ALTER TABLE deportivo_partido RENAME COLUMN tipo_legacy TO tipo;",
        ),

        # --- 2. Renombrar condicion → condicion_legacy (VARCHAR → VARCHAR) ---
        migrations.RunSQL(
            sql="ALTER TABLE deportivo_partido RENAME COLUMN condicion TO condicion_legacy;",
            reverse_sql="ALTER TABLE deportivo_partido RENAME COLUMN condicion_legacy TO condicion;",
        ),

        # --- 3. Eliminar resultado de la BD (viola 3NF - es calculable) ---
        migrations.RunSQL(
            sql="ALTER TABLE deportivo_partido DROP COLUMN IF EXISTS resultado;",
            reverse_sql="ALTER TABLE deportivo_partido ADD COLUMN resultado VARCHAR(20);",
        ),

        # --- 4. Agregar nueva FK tipo_id → core_cattipopartido ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE deportivo_partido
                ADD COLUMN IF NOT EXISTS tipo_id INTEGER
                    REFERENCES core_cattipopartido(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="ALTER TABLE deportivo_partido DROP COLUMN IF EXISTS tipo_id;",
        ),

        # --- 5. Agregar nueva FK condicion_id → core_catcondicionpartido ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE deportivo_partido
                ADD COLUMN IF NOT EXISTS condicion_id INTEGER
                    REFERENCES core_catcondicionpartido(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="ALTER TABLE deportivo_partido DROP COLUMN IF EXISTS condicion_id;",
        ),

        # --- 6. Sincronizar estado del ORM de Django sin re-ejecutar SQL ---
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='partido',
                    name='tipo',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='partidos',
                        to='core.cattipopartido',
                    ),
                ),
                migrations.AlterField(
                    model_name='partido',
                    name='condicion',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='partidos',
                        to='core.catcondicionpartido',
                    ),
                ),
                # Registrar tipo_legacy y condicion_legacy como campos FK locales
                migrations.AddField(
                    model_name='partido',
                    name='tipo_legacy',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='partidos_legacy',
                        to='deportivo.cat_tipopartido',
                    ),
                ),
                migrations.AddField(
                    model_name='partido',
                    name='condicion_legacy',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='partidos_legacy',
                        to='deportivo.cat_condicionpartido',
                    ),
                ),
            ],
            database_operations=[],  # Ya ejecutado vía RunSQL
        ),
    ]
