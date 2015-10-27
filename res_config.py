# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#    Copyright (C) 2013-today Synconics Technologies Pvt. Ltd. (<http://www.synconics.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields

class wcfmc_config_settings(osv.osv_memory):
    _inherit = 'base.config.settings'
    _columns = {
        'user_name': fields.char('User Name',size=24),
        'password': fields.char('Password',size=24),
        'runscope_auth_token' : fields.char('Authentication Token',size=32),
    }

    def get_default_wcfmc(self, cr, uid, fields, context=None):
        params = self.pool.get('ir.config_parameter')
        user_name = params.get_param(cr, uid, 'wcfmc_username',default='',context=context)
        password = params.get_param(cr, uid, 'wcfmc_password',default='',context=context)
        runscope_auth_token = params.get_param(cr, uid, 'wcfmc_auth_token',default='',context=context)
        return dict(user_name=user_name,password=password,runscope_auth_token=runscope_auth_token)
        

    def set_default_wcfmc(self, cr, uid, ids, context=None):
        params = self.pool['ir.config_parameter']
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'wcfmc_username', (myself.user_name or '').strip(),context=None)
        params.set_param(cr, uid, 'wcfmc_password', (myself.password or '').strip(),context=None)
        params.set_param(cr, uid, 'wcfmc_auth_token', (myself.runscope_auth_token or '').strip(),context=None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
