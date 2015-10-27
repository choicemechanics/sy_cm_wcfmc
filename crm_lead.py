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

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    wcfmc_id =fields.Integer('WCFMC')
    car_registration = fields.Char('Registration No',size=8)
    make_model = fields.Char('Model',size=64)
    fuel = fields.Selection([('petrol','Petrol'),('diesel','Diesel')],'Fuel Type')
    transmission = fields.Selection([('manual','Manual'),('automatic','Automatic')],'Transmission')
    registration_year = fields.Integer('Registration year')
    city = fields.Char('City',size=45)
    postcode = fields.Char('Postcode',size=8)

    @api.model
    def create(self,vals):
        sale_obj = self.env['sale.order']
        product_obj = self.env['product.product']
        sale_line_obj = self.env['sale.order.line']
        case = super(crm_lead,self).create(vals)
        if case.partner_id and case.wcfmc_id and not case.description and case.name and case.postcode:                        
            values = {
                    'city' : case.city or False,
                    'registration_year' : case.registration_year or False,
                    'fuel' : case.fuel or False,
                    'transmission' : case.transmission or False,
                    'car_registration' : case.car_registration  or False,
                    'make_model' : case.make_model or False,
                    'wcfmc_id' : case.wcfmc_id or False,                        
                    'postcode' : case.postcode or False,
                    'partner_id':case.partner_id and case.partner_id.id or False,
                }
            cm_postcodes = self.env['cm.postcode'].search([('part_1_portion','=',case.postcode[:3])])
            product_template = self.env['product.template'].search([('wcfmc_job_name','=',case.name)])
            products = product_obj.search([('product_tmpl_id','in',product_template.ids)])
            if products and cm_postcodes:
                order_line = []
                for product in products:
                    product_default_data = sale_line_obj.product_id_change(pricelist=case.partner_id.property_product_pricelist.id ,product=product.id,partner_id=case.partner_id.id)['value']
                    product_default_data.update({'price_unit':1.0,'product_id':product.id})
                    order_line.append([0,False,product_default_data])
                    if order_line:
                        values.update({'order_line':order_line})
                sale_id = sale_obj.create(values)
                case.write({'ref': 'sale.order,%s' % sale_id.id})
                state = self.env['crm.case.stage'].search([('name','ilike','Quoted')])
                if state:
                    case.write({'stage_id':state.id})
        return case

    @api.v7
    def get_new_lead(self,cr,uid,context=None):
        pass
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: