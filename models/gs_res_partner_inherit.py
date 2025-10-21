# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import timedelta
from odoo.exceptions import ValidationError

class GsResPartnerInherit(models.Model):
    _inherit = "res.partner"

    binding_type = fields.Selection([('micro', 'Microempresa(de 1 a 10 empleados)'),
        ('pequeña', 'Pequeña empresa(de 11 a 50 empleados)'),
        ('mediana', 'Mediana empresa(de 51 a 250 empleados)'),
        ('gran', 'Gran empresa(más de 200 empleados)')])

    gs_presupuesto = fields.Float(string="Presupuesto")
    gs_estado_cliente = fields.Selection([
        ('cliente_nuevo', 'Cliente nuevo'),
        ('cliente_recurrente', 'Cliente recurrente'),
        ('cliente_inactivo', 'Cliente inactivo'),
        ('cliente_perdido', 'Cliente perdido'),
        ('cliente_recuperado', 'Cliente recuperado'),
    ], string="Estado del cliente")
    gs_fecha_actualizacion_documentos = fields.Date(string="Fecha de actualización de documentos")
    gs_productos_comprados = fields.Many2many('product.product', string="Productos comprados")
    gs_no_proyecto = fields.Char(string="No. Proyecto")
    gs_estado_proyecto = fields.Selection([
        ('modelado', 'Modelado'),
        ('interiorismo', 'Interiorismo'),
        ('proyecto_renderizado', 'Proyecto Renderizado'),
        ('primera_entrega', 'Primera entrega'),
        ('entrega_final', 'Entrega Final'),
        ('cerrado', 'Cerrado'),
        ('calificado', 'Calificado'),
    ], string="Estado del proyecto")

    gs_proxima_actividad = fields.Selection([
        ('reunion', 'Reunion'),
        ('llamada', 'Llamada'),
        ('correo', 'Correo'),
        ('whatsapp', 'Mensaje WhatsApp'),
    ], string="Proxima actividad")
    gs_proxima_fecha = fields.Datetime(string="Fecha de la proxima actividad")
    gs_facturacion = fields.Char(string="Facturación")
    gs_pagos = fields.Char(string="Pagos")

