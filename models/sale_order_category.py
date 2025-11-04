from odoo import models, fields

class SaleOrderCategory(models.Model):
    _name = 'sale.order.category'
    _description = 'Categoría de Pedido de Venta'

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean(string="Activo", default=True)
    description = fields.Text(string="Descripción")

class SaleOrderForm(models.Model):
    _inherit = 'sale.order'

    category_ids = fields.Many2many(
        'sale.order.category',
        'sale_order_category_rel',
        'order_id', 'category_id',
        string="Categorías"
    )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dias_habiles = fields.Char(string='Días hábiles')