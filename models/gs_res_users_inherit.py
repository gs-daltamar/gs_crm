from odoo import models, fields

class GsResUsersInherit(models.Model):
    _inherit = 'res.users'

    gs_is_sales_manager = fields.Boolean(string='Gerente de Ventas')
