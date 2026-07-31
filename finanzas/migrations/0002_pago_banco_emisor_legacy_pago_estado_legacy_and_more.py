# Migración manual - Fase 4 App: finanzas
# La BD real tiene banco_emisor, estado, metodo como VARCHAR (choices de texto),
# pagada como BOOLEAN real, y no existen las tablas de catálogos locales.
# Esta migración:
# 1. Renombra banco_emisor/estado/metodo a _legacy (VARCHAR → VARCHAR)
# 2. Agrega nuevas FK hacia core (banco_emisor_id, estado_id, metodo_id)
# 3. Elimina pagada de la BD (viola 3NF - dependencia transitiva vía pago.estado)
# 4. Corrige el on_delete de PagoAuditLog.actor a SET_NULL
# 5. Amplía max_length de fuente en TasaBCV a 50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_poblar_catalogos'),
        ('finanzas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # === TABLA finanzas_pago ===

        # --- 1. Renombrar banco_emisor → banco_emisor_legacy ---
        migrations.RunSQL(
            sql="ALTER TABLE finanzas_pago RENAME COLUMN banco_emisor TO banco_emisor_legacy;",
            reverse_sql="ALTER TABLE finanzas_pago RENAME COLUMN banco_emisor_legacy TO banco_emisor;",
        ),

        # --- 2. Renombrar estado → estado_legacy ---
        migrations.RunSQL(
            sql="ALTER TABLE finanzas_pago RENAME COLUMN estado TO estado_legacy;",
            reverse_sql="ALTER TABLE finanzas_pago RENAME COLUMN estado_legacy TO estado;",
        ),

        # --- 3. Renombrar metodo → metodo_legacy ---
        migrations.RunSQL(
            sql="ALTER TABLE finanzas_pago RENAME COLUMN metodo TO metodo_legacy;",
            reverse_sql="ALTER TABLE finanzas_pago RENAME COLUMN metodo_legacy TO metodo;",
        ),

        # --- 4. Agregar nueva FK banco_emisor_id → core_catbanco ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE finanzas_pago
                ADD COLUMN IF NOT EXISTS banco_emisor_id INTEGER
                    REFERENCES core_catbanco(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="ALTER TABLE finanzas_pago DROP COLUMN IF EXISTS banco_emisor_id;",
        ),

        # --- 5. Agregar nueva FK estado_id → core_catestadopago ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE finanzas_pago
                ADD COLUMN IF NOT EXISTS estado_id INTEGER
                    REFERENCES core_catestadopago(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="ALTER TABLE finanzas_pago DROP COLUMN IF EXISTS estado_id;",
        ),

        # --- 6. Agregar nueva FK metodo_id → core_catmetodopago ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE finanzas_pago
                ADD COLUMN IF NOT EXISTS metodo_id INTEGER
                    REFERENCES core_catmetodopago(id)
                    ON DELETE RESTRICT
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="ALTER TABLE finanzas_pago DROP COLUMN IF EXISTS metodo_id;",
        ),

        # === TABLA finanzas_mensualidad ===

        # --- 7. Eliminar pagada de la BD (viola 3NF - dependencia transitiva) ---
        migrations.RunSQL(
            sql="ALTER TABLE finanzas_mensualidad DROP COLUMN IF EXISTS pagada;",
            reverse_sql="ALTER TABLE finanzas_mensualidad ADD COLUMN pagada BOOLEAN NOT NULL DEFAULT FALSE;",
        ),

        # === TABLA finanzas_pagoauditlog ===

        # --- 8. Corregir on_delete de actor: PROTECT → SET_NULL (ya es nullable) ---
        # El constraint de FK se reemplaza via AlterField estándar (sí aplica aquí
        # porque el cambio es solo en el constraint, no en el tipo de columna).
        migrations.AlterField(
            model_name='pagoauditlog',
            name='actor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='pagos_audit',
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        # === TABLA finanzas_tasabcv ===

        # --- 9. Ampliar max_length de fuente a 50 (ERD V2.2) ---
        migrations.AlterField(
            model_name='tasabcv',
            name='fuente',
            field=models.CharField(
                default='dolarapi',
                help_text='Origen: dolarapi, manual, etc.',
                max_length=50,
            ),
        ),

        # --- 10. Sincronizar estado del ORM sin re-ejecutar SQL ---
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='pago',
                    name='banco_emisor',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pagos',
                        to='core.catbanco',
                    ),
                ),
                migrations.AlterField(
                    model_name='pago',
                    name='estado',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pagos',
                        to='core.catestadopago',
                    ),
                ),
                migrations.AlterField(
                    model_name='pago',
                    name='metodo',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pagos',
                        to='core.catmetodopago',
                    ),
                ),
                # Registrar los campos _legacy en el ORM
                migrations.AddField(
                    model_name='pago',
                    name='banco_emisor_legacy',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pagos_legacy',
                        to='finanzas.cat_banco',
                    ),
                ),
                migrations.AddField(
                    model_name='pago',
                    name='estado_legacy',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pagos_legacy',
                        to='finanzas.cat_estadopago',
                    ),
                ),
                migrations.AddField(
                    model_name='pago',
                    name='metodo_legacy',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='pagos_legacy',
                        to='finanzas.cat_metodopago',
                    ),
                ),
            ],
            database_operations=[],  # Ya ejecutado vía RunSQL
        ),
    ]
