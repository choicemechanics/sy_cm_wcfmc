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

    wcfmc_id =fields.Many2one('cm.whocanfixmycar','WCFMC')
    car_registration = fields.Char('Registration No',size=8)
    make_model = fields.Char('Model',size=64)
    fuel = fields.Selection([('petrol','Petrol'),('diesel','Diesel')],'Fuel Type')
    transmission = fields.Selection([('manual','Manual'),('automatic','Automatic')],'Transmission')
    registration_year = fields.Integer('Registration year')
    city = fields.Char('City',size=45)
    postcode = fields.Char('Postcode',size=8)

    @api.v7
    def get_new_lead(self,cr,uid,ids,context=None):
        pass


from openerp.osv import fields, osv
from openerp.tools.translate import _

class crm_make_sale(osv.osv_memory):

    _inherit = "crm.make.sale"

    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context = dict(context or {})
        context.pop('default_state', False)        
        
        vals = {}
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        sale_line_obj = self.pool.get('sale.order.line')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))
                
                vals.update({
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.datetime.now(),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                })

                if case.wcfmc_id and not case.description and case.name and case.postcode:                        
                    vals.update({
                            'city' : case.city  or False,
                            'registration_year' : case.registration_year  or False,
                            'fuel' : case.fuel  or False,
                            'transmission' : case.transmission  or False,
                            'car_registration' : case.car_registration  or False,
                            'make_model' : case.make_model  or False,
                            'wcfmc_id' : case.wcfmc_id and case.wcfmc_id.id or False,                        
                            'postcode' : case.postcode  or False,
                        })
                    cm_postcodes = self.pool.get('cm.postcode').search(cr,uid,[('part_1_portion','=',case.postcode[:3])],context=context)
                    products = self.pool.get('product.product').search(cr,uid,[('wcfmc_job_name','=',case.name)],context=context)
                    if products and cm_postcodes:
                        order_line = []
                        for product in products:
                            product_default_data = sale_line_obj.product_id_change(cr,uid,False, pricelist, product,partner_id=partner.id,context=context)['value']
                            product_default_data.update({'price_unit':1.0,'product_id':product})
                            order_line.append([0,False,product_default_data])
                            if order_line:
                                vals.update({'order_line':order_line})
                        state = self.pool.get('crm.case.stage').search(cr,uid,[('name','ilike','Quoted')],context=context)
                        if state:
                            case_obj.write(cr, uid, [case.id], {'stage_id':state[0]})

                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)

                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
                
            if make.close:
                case_obj.case_mark_won(cr, uid, data, context=context)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value