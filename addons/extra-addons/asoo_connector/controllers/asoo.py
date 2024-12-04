# -*- coding: utf-8 -*-
import uuid
from datetime import datetime, timedelta

from odoo import fields, SUPERUSER_ID, api

from odoo.addons.web.controllers.utils import _get_login_redirect_url
from odoo.http import request
from odoo import registry as registry_get
from odoo.tools import config
from odoo.exceptions import AccessDenied
from odoo.http import route, Controller

TOKEN_EXPIRE_SECONDS = 30


class Asoo(Controller):

    @route('/asoo/auth/token', type='json', auth='none')
    def generate_token(self, db, admin_pwd, login):
        if not config.verify_admin_password(admin_pwd):
            raise AccessDenied()

        registry = registry_get(db)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            token = uuid.uuid4()
            user = env['res.users'].sudo().search([('login', '=', login)])
            user.write({
                'asoo_auth_token': token,
                'asoo_auth_token_expire': datetime.now() + timedelta(
                    seconds=TOKEN_EXPIRE_SECONDS
                )
            })
        return token

    @route('/asoo/auth/signin', type='http', auth='none')
    def signin(self, **kw):
        token = kw.get('token')
        db = kw.get('db')
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Get user by token
            user = env['res.users'].sudo().search([
                ('asoo_auth_token', '=', token)
            ])
            if not user:
                raise AccessDenied()

            # Check if expire
            if fields.Datetime.from_string(
                user.asoo_auth_token_expire
            ) < datetime.now():
                raise AccessDenied()

            # Login
            uid = request.session.authenticate(
                db,
                user.login,
                user.asoo_auth_token
            )

            # Clean token
            user.write({
                'asoo_auth_token': False,
                'asoo_auth_token_expire': False
            })
            cr.commit()

            # Redirection
            return _get_login_redirect_url(uid, request.redirect('/web'))
