# controllers/portal_login.py
from odoo.http import request, route, Controller
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import Unauthorized


def _ensure_session_db():
    if request.session.db:
        return
    default_db = config.get('db_name')
    if default_db:
        request.session.db = default_db
        return
    try:
        dbs = db_service.list_dbs() or []
    except Exception:
        dbs = []
    if dbs:
        request.session.db = dbs[0]
    else:
        return request.redirect('/web/database/selector')
class IndexLogin(Controller):

    @route('/portal_login', auth='public', website=True, csrf=True, methods=['GET', 'POST'])
    def portal_login(self, **kw):

        _ensure_session_db()
        print(_ensure_session_db())

        error = None
        if request.httprequest.method == 'POST':
            login = kw.get('login')
            password = kw.get('password')
            try:
                uid = request.session.authenticate(login, password)
                user = request.env['res.users'].sudo().browse(uid)
                if uid:
                    return request.redirect('/client_portal')

            except (AccessDenied, Unauthorized):
                error = "Correo o contraseña inválidos"

        return request.render('gs_crm.gs_login_template', {'error': error, })

    @route('/portal_logout', auth='user', website=True)
    def portal_logout(self, **kw):
        request.session.logout(keep_db=True)
        return request.redirect('/portal_login')
