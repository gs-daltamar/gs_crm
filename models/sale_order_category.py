from odoo import models, fields

class SaleOrderCategory(models.Model):
    _name = 'sale.order.category'
    _description = 'Categoría de Pedido de Venta'

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean(string="Activo", default=True)
    description = fields.Html(
        string="Minuta / Cláusulas (HTML)",
        sanitize=True,
        translate=True,
        help="Contenido (minuta) que se insertará en el contrato de las órdenes que usen esta categoría."
    )

class SaleOrderForm(models.Model):
    _inherit = 'sale.order'

    category_ids = fields.Many2many(
        'sale.order.category',
        'sale_order_category_rel',
        'order_id', 'category_id',
        string="Categorías"
    )

    def action_edit_contract_categories(self):
        self.ensure_one()
        action = self.env.ref('gs_crm.action_sale_order_categories_edit_for_order').read()[0]
        action['domain'] = [('id', 'in', self.category_ids.ids)]
        # Contexto: edición directa y volver a la SO al cerrar
        action['context'] = {
            'default_active': True,
            'search_default_filter_my_categories': 0,
        }
        return action

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dias_habiles = fields.Char(string='Días hábiles')