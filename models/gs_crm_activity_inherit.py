# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import timedelta
from odoo.exceptions import ValidationError



class GsCrmActivityInherit(models.Model):
    _inherit = "mail.activity"

    reminder_24h_sent = fields.Boolean(
        string="Recordatorio 24h enviado",
        default=False,
        help="Para no reenviar múltiples recordatorios por la misma actividad."
    )

    @api.model
    def _cron_send_24h_reminders(self):

        # Fech
        target_date = date.today() + timedelta(days=1)

        # Busca actividades vigentes con fecha mañana y sin recordatorio enviado
        activities = self.search([
            ("date_deadline", "=", target_date),
            ("reminder_24h_sent", "=", False),
            # Por si acaso: actividades eliminadas al marcar como realizadas ya no estarán aquí.
        ])

        if not activities:
            return

        template = self.env.ref(
            "gs_activity_reminder_24h.mail_template_activity_reminder_24h",
            raise_if_not_found=False
        )

        # Group by user para mensajes más ordenados
        for act in activities:
            user = act.user_id
            if not user or not user.partner_id:
                continue

            # Notificación en Odoo (chatter) sobre el registro asociado:
            # Si hay registro destino, posteamos allí; si no, en el hilo genérico.
            body = _(
                "<p><b>Recordatorio 24h</b></p>"
                "<p>Tienes una actividad programada para <b>%s</b> en el modelo <b>%s</b>.</p>"
                "<p><b>Resumen:</b> %s</p>"
            ) % (
                fields.Date.to_string(act.date_deadline or target_date),
                act.res_model or "N/A",
                act.summary or _("(Sin resumen)")
            )

            # Si la actividad tiene un destino (res_id), posteamos en ese registro para que quede la trazabilidad
            if act.res_model and act.res_id:
                record = self.env[act.res_model].browse(act.res_id)
                try:
                    record.message_post(
                        body=body,
                        partner_ids=[user.partner_id.id],
                        message_type="notification",
                        subtype_xmlid="mail.mt_note",
                    )
                except Exception:
                    pass

            # Email (si hay plantilla configurada y el usuario tiene email)
            if template and user.partner_id.email:
                try:
                    # Enviamos la plantilla contra el propio registro de actividad
                    # para poder referenciar campos (summary, date_deadline, etc.)
                    template.send_mail(act.id, force_send=True, raise_exception=False)
                except Exception:
                    # No rompemos el cron si hay un problema de email
                    pass
            # Marcamos que ya enviamos el recordatorio
            act.reminder_24h_sent = True