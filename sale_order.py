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

from openerp import fields, models, api, _

class sale_order(models.Model):
    _inherit = 'sale.order'

    wcfmc_id = fields.Integer('WCFMC')
    car_registration = fields.Char('Registration No',size=8)
    make_model = fields.Char('Model',size=64)
    fuel = fields.Selection([('petrol','Petrol'),('diesel','Diesel')],'Fuel Type')
    transmission = fields.Selection([('manual','Manual'),('automatic','Automatic')],'Transmission')
    registration_year = fields.Integer('Registration year')
    city = fields.Char('City',size=45)
    postcode = fields.Char('Postcode',size=8)

    @api.model
    def create(self,vals):
        res = super(sale_order,self).create(vals)
        # This is where the quotation will be imported into Zoho Creator
        if res.state == 'draft' and res.wcfmc_id:
            pass
        return res

    @api.v7
    def update_quotations(self,cr,uid,context=None):
        pass
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: