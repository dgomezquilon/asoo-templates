# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

from odoo.addons.web.controllers.dataset import DataSet
from odoo.tools import config
from odoo.exceptions import AccessDenied
from odoo import http
from odoo import registry
from odoo.api import call_kw
from odoo.models import check_method_name


class DataSet(DataSet):

    @http.route([
        '/asoo/web/dataset/call_kw',
    ], type='json', auth='none')
    def asoo_call(self, db, admin_pwd, params):
        if not config.verify_admin_password(admin_pwd):
            raise AccessDenied()

        with registry(db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            model, method, args, kwargs = params
            check_method_name(method)
            return call_kw(env[model], method, args, kwargs)
