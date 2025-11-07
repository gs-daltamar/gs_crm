# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller
from odoo.exceptions import AccessDenied
import base64
from odoo.fields import Datetime as FDatetime
import json
from odoo import http
from werkzeug.wrappers import Response



import mimetypes


class GSPortalDashboard(Controller):

    @route('/client_portal', auth='user', website=True, methods=['GET'])
    def client_portal_home(self, **kw):
        user = request.env.user
        partner = user.partner_id.sudo()

        last_login_str = None
        if user.login_date:
            dt_tz = FDatetime.context_timestamp(user, user.login_date)
            last_login_str = dt_tz.strftime('%d-%m-%Y %H:%M')

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
            if photo.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
                return request.redirect('/client_portal')
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
        return request.redirect('/client_portal')

    @route('/client_portal/delete_attachment/<int:att_id>', auth='user', website=True, csrf=True, methods=['POST'])
    def client_portal_delete_attachment(self, att_id, **kw):
        att = request.env['ir.attachment'].sudo().browse(att_id)
        partner = request.env.user.partner_id.sudo()
        if att and att.res_model == 'res.partner' and att.res_id == partner.id:
            att.unlink()
        return request.redirect('/client_portal')

    @http.route('/gs_crm/update_contract_categories', type='json', auth='user', methods=['POST'])
    def update_contract_categories(self, **post):
        # --- Robustez: parseo manual del body JSON, aunque sea type="json"
        data = {}
        try:
            # Primero intenta json.loads sobre el raw body
            raw = request.httprequest.get_data(cache=False, as_text=True)  # str
            if raw:
                data = json.loads(raw)
        except Exception:
            # Fallbacks opcionales (por si tu server cambia comportamiento)
            data = getattr(request, 'jsonrequest', {}) or {}

        so_id = data.get('so_id')
        items = data.get('items', [])

        # Validación básica
        if not so_id or not isinstance(items, list):
            return {'error': 'Missing data'}

        # Solo usuarios internos
        if not request.env.user.has_group('base.group_user'):
            return {'error': 'forbidden'}

        so = request.env['sale.order'].sudo().browse(int(so_id))
        if not so.exists():
            return {'error': 'SO not found'}

        allowed = set(so.category_ids.ids)

        for it in items:
            cid = int(it.get('id'))
            if cid not in allowed:
                continue
            request.env['sale.order.category'].sudo().browse(cid).write({
                'description': it.get('description', ''),
            })

        return {'status': 'ok'}
