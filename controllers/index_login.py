# controllers/portal_login.py
from odoo.http import request, route, Controller
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import Unauthorized

class IndexLogin(Controller):

    @route('/portal_login', auth='public', website=True, csrf=True, methods=['GET', 'POST'])
    def portal_login(self, **kw):
        redirect_to = kw.get('redirect') or '/client_portal'
        if not request.env.user._is_public():
            return request.redirect(redirect_to)

        error = None
        if request.httprequest.method == 'POST':
            login = (kw.get('login') or '').strip()
            password = kw.get('password') or ''
            try:
                uid = request.session.authenticate(login, password)  # Odoo 18
                if uid:
                    return request.redirect(redirect_to)
            except (AccessDenied, Unauthorized):
                error = "Correo o contraseña inválidos"

        return request.render('gs_crm.gs_login_template', {'error': error, 'redirect': redirect_to})

    @route('/portal_logout', auth='user', website=True)
    def portal_logout(self, **kw):
        request.session.logout(keep_db=True)
        return request.redirect('/portal_login')
