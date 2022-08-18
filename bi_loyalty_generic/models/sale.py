# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError,Warning
import logging
import math

_logger = logging.getLogger(__name__)

class web_category(models.Model):
	_inherit = 'product.category'

	Minimum_amount  = fields.Integer("Amount For loyalty Points")
	amount_footer = fields.Integer('Amount', related='Minimum_amount')

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	order_credit_points = fields.Integer(string='Order Credit Points',copy=False)
	order_redeem_points = fields.Integer(string='Order Redeemed Points',copy=False)
	redeem_value = fields.Float(string='Redeem point value',copy=False)
	is_from_website = fields.Boolean("Is from Website",copy=False,readonly=True)
	total_sales = fields.Float(string='Total Sales',compute= 'update_total_sale')

	def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
		res = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
		if res.get('quantity') != 0 :
			self.ensure_one()
			OrderLine = self.env['sale.order.line']
			line = OrderLine.sudo().browse(line_id)
			if line and line.discount_line and line.order_id.redeem_value:
				today_date = datetime.today().date()	
				loyalty_config = self.env['all.loyalty.setting'].sudo().search([('active','=',True),('issue_date', '<=', today_date ),
									('expiry_date', '>=', today_date )])
				for config in loyalty_config:
					if config:	
						if config.loyalty_tier.min_range <= line.order_id.total_sales <= config.loyalty_tier.max_range:
							for rule in config.redeem_ids:
								if rule.min_amt <= line.order_id.partner_id.loyalty_points  and   line.order_id.partner_id.loyalty_points <= rule.max_amt :
									line.write({
										'price_unit': - (line.redeem_points * line.order_id.redeem_value)/rule.points_redeem
									})
		return res

	def update_total_sale(self):
		for record in self:
			sale_id = self.search([('partner_id','=', record.partner_id.id)])
			total_sale = 0
			if sale_id:
				total_sale = sum(order.amount_total for order in sale_id)
			record.total_sales = total_sale

	@api.constrains('total_sales')
	def update_loyalty_tier(self):
		for record in self:
			res_id = self.env['loyalty.tier.config'].search([('min_range', '<=', record.total_sales),('max_range', '>=', record.total_sales)])
			if res_id:
				loyalty_config_id = self.env['all.loyalty.setting'].search([('loyalty_tier.tier_name','=',res_id.tier_name)])
				if loyalty_config_id.loyality_amount:
					record.order_credit_points = record.total_sales / loyalty_config_id.loyality_amount

	@api.model
	def create(self, vals):
		result = super(SaleOrder, self).create(vals)
		if self.env.company.promotion_id:
			if self.env.company.from_date <= (result.create_date).date() <= self.env.company.to_date:
				if self.env.company.product_type == 'product':
					for line in result.order_line:
						if line.product_id in self.env.company.product_ids:
							line.order_id.write({'order_credit_points':result.order_credit_points + self.env.company.promotion_points})
				if self.env.company.product_type == 'product_category':
					for line in result.order_line:
						if line.product_id.categ_id in self.env.company.product_category_ids:
							line.order_id.write({'order_credit_points':result.order_credit_points + self.env.company.promotion_points})
		loyalty_history = self.env['all.loyalty.history'].search([('partner_id','=',result.partner_id.id)])
		if self.env.company.sign_up_bonus:
			if not loyalty_history:
				vals = {
					'partner_id':result.partner_id.id,
					'points':self.env.user.company_id.sign_up_bonus,
					'state' : 'done',
					'transaction_type' : 'credit'
				}
				self.env['all.loyalty.history'].create(vals)
		return result

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	discount_line = fields.Boolean(string='Discount line',readonly=True,copy=False)
	redeem_points = fields.Integer(string='Redeem Points',copy=False)
	redeem_value = fields.Float(string='Redeem point value',copy=False)
