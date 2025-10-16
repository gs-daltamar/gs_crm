# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import timedelta
from odoo.exceptions import ValidationError


class GsCrmLeadInherit(models.Model):
    _inherit = "crm.lead"

    gs_last_activity_time = fields.Datetime(string="Ultima actividad", default=fields.Datetime.now)
    gs_activity_status = fields.Selection([
        ('green', 'Verde'),
        ('yellow', 'Amarillo'),
        ('red', 'Rojo'),
        ('black', 'Negro')
    ], string="Estado de actividad")

    def write(self, vals):
        if any(field in vals for field in ['description', 'stage_id', 'user_id']):
            vals['gs_last_activity_time'] = fields.Datetime.now()
        return super().write(vals)

    def _notify_sanction(self):
        partner_ids = []

        # Asegurarse de que el usuario y su partner existan
        if self.user_id and self.user_id.partner_id:
            partner_ids.append(self.user_id.partner_id.id)

        # Asegurarse de que el gerente y su partner existan
        if self.user_id and self.user_id.parent_id and self.user_id.parent_id.partner_id:
            partner_ids.append(self.user_id.parent_id.partner_id.id)

        # Solo enviar notificación si hay destinatarios válidos
        if partner_ids:
            self.message_post(
                body=f"¡Sanción! Lead sin gestión por más de 5 minutos: {self.name}",
                partner_ids=partner_ids
            )

    def check_lead_activity(self):
        closed_stages = [4, 5]  # IDs de etapas cerradas
        leads = self.search([('stage_id', 'not in', closed_stages)])

        for lead in leads:
            if not lead.gs_last_activity_time:
                continue

            # Cálculo en minutos para pruebas
            inactive_minutes = (fields.Datetime.now() - lead.gs_last_activity_time).total_seconds() / 3600

            # Umbrales en minutos para pruebas rápidas
            if inactive_minutes > 12:  # Más de 5 minutos -> Negro
                lead.gs_activity_status = 'black'
                lead._notify_sanction()
            elif inactive_minutes > 4:  # Entre 3-5 minutos -> Rojo
                lead.gs_activity_status = 'red'
            elif inactive_minutes > 2:  # Entre 1-3 minutos -> Amarillo
                lead.gs_activity_status = 'yellow'
            else:  # Menos de 1 minuto -> Verde
                lead.gs_activity_status = 'green'

    @api.model
    def _register_hook(self):
        """Se ejecuta al iniciar el servidor, crea el cron job si no existe"""
        super()._register_hook()

        # Buscar si el cron job ya existe
        cron = self.env['ir.cron'].sudo().search([
            ('cron_name', '=', 'Monitoreo de actividad de leads'),
        ], limit=1)

        # Si no existe, crearlo
        if not cron:
            # Primero creamos la acción del servidor
            server_action = self.env['ir.actions.server'].sudo().create({
                'name': 'Monitoreo de actividad de leads',
                'model_id': self.env['ir.model'].sudo().search([('model', '=', 'crm.lead')], limit=1).id,
                'state': 'code',
                'code': 'env["crm.lead"].check_lead_activity()',
            })

            self.env['ir.cron'].sudo().create({
                'ir_actions_server_id': server_action.id,
                'user_id': self.env.ref('base.user_root').id,
                'interval_number': 2,
                'interval_type': 'hours',
                'nextcall': fields.Datetime.now(),
                'priority': 5,
                'active': True,
            })

    @api.constrains('phone')
    def check_unique_phone(self):
        for record in self:
            if not record.phone:
                continue

            #limpiar telefono y quitar espacios
            cleaned_phone = record.phone.replace(' ', '').strip()

            #buscamos otros leads con el mismo telefono
            existing = self.search([
                ('id', '!=', record.id),
                ('phone', '=', cleaned_phone)
            ])
            for lead in existing:
                if lead.phone:
                    raise ValidationError("El número de teléfono debe ser único")


