# -*- coding: utf-8 -*-
# from odoo import http


# class GsCrm(http.Controller):
#     @http.route('/gs_crm/gs_crm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gs_crm/gs_crm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gs_crm.listing', {
#             'root': '/gs_crm/gs_crm',
#             'objects': http.request.env['gs_crm.gs_crm'].search([]),
#         })

#     @http.route('/gs_crm/gs_crm/objects/<model("gs_crm.gs_crm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gs_crm.object', {
#             'object': obj
#         })

