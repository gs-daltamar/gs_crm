# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller
from odoo.exceptions import AccessDenied
import base64
from odoo.fields import Datetime as FDatetime

import mimetypes

class GSPortalDashboard(Controller):

    @route('/client_portal', auth='user', website=True, methods=['GET'])
    def client_portal_home(self, **kw):
        user = request.env.user
        partner = user.partner_id.sudo()

        # Último login con TZ
        last_login_str = None
        if user.login_date:
            dt_tz = FDatetime.context_timestamp(user, user.login_date)
            last_login_str = dt_tz.strftime('%d-%m-%Y %H:%M')


        # Adjuntos del partner (solo últimos 10 para mostrar)
        attachments = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', partner.id),
        ], order="create_date desc", limit=10)

        return request.render('gs_crm.portal_dashboard', {
            'partner': partner,
            'attachments': attachments,
            'last_login_str': last_login_str,

        })

    @route('/client_portal/save_profile', auth='user', website=True, csrf=True, methods=['POST'])
    def client_portal_save_profile(self, **post):
        partner = request.env.user.partner_id.sudo()
        vals = {}
        # mapea inputs permitidos -> campos res.partner
        field_map = {
            'name': 'name',
            'email': 'email',
            'phone': 'phone',
            'mobile': 'mobile',
            'street': 'street',
            'city': 'city',
            'zip': 'zip',
        }
        for k, field in field_map.items():
            if k in post:
                vals[field] = post[k].strip()
        if 'country_id' in post and post['country_id']:
            vals['country_id'] = int(post['country_id'])
        if 'state_id' in post and post['state_id']:
            vals['state_id'] = int(post['state_id'])
        if vals:
            partner.write(vals)
        return request.redirect('/client_portal')

    @route('/client_portal/upload_photo', type='http', auth='user', website=True, csrf=True, methods=['POST'])
    def client_portal_upload_photo(self, **post):
        partner = request.env.user.partner_id.sudo()
        photo = post.get('photo')
        if photo and hasattr(photo, 'filename'):
            # patrón de subida a image_1920 como ya hiciste en otros portales
            # (leer, validar tipo, base64 y write al partner) :contentReference[oaicite:2]{index=2}
            if photo.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
                return request.redirect('/client_portal')  # podrías mostrar un toast
            data64 = base64.b64encode(photo.read())
            partner.write({'image_1920': data64})
        return request.redirect('/client_portal')

    @route('/client_portal/upload_document', type='http', auth='user', website=True, csrf=True, methods=['POST'])
    def client_portal_upload_document(self, **post):
        partner = request.env.user.partner_id.sudo()
        up = post.get('file')
        if up and hasattr(up, 'filename'):
            mimetype, _ = mimetypes.guess_type(up.filename)
            att = request.env['ir.attachment'].sudo().create({
                'name': up.filename,
                'datas': base64.b64encode(up.read()),
                'mimetype': mimetype or 'application/octet-stream',
                'res_model': 'res.partner',
                'res_id': partner.id,
            })
            # si más adelante quieres crear documents.document, es el mismo patrón que ya usas. :contentReference[oaicite:3]{index=3}
        return request.redirect('/client_portal')

    @route('/client_portal/delete_attachment/<int:att_id>', auth='user', website=True, csrf=True, methods=['POST'])
    def client_portal_delete_attachment(self, att_id, **kw):
        att = request.env['ir.attachment'].sudo().browse(att_id)
        partner = request.env.user.partner_id.sudo()
        # seguridad básica: solo borrar si pertenece a este partner
        if att and att.res_model == 'res.partner' and att.res_id == partner.id:
            att.unlink()
        return request.redirect('/client_portal')
