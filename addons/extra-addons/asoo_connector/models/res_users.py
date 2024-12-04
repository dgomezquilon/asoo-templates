# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_admin = fields.Boolean(compute='_compute_is_admin', store=True)
    asoo_auth_token = fields.Char('Asoo Auth token')
    asoo_auth_token_expire = fields.Datetime('Asoo Auth token expire at')

    @api.depends('groups_id')
    def _compute_is_admin(self):
        for rec in self:
            rec.is_admin = rec.has_group('base.group_system')

    def _check_credentials(self, password, env):
        try:
            super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            user = self.sudo().search([
                ('id', '=', self._uid),
                ('asoo_auth_token', '=', password)
            ])
            if not user:
                raise
