

from odoo import models, fields, api, _,tools
from datetime import datetime, timedelta

class ManuallyLoyalty(models.TransientModel):
	_name = 'loyalty.wizard.manually'
	_description = "Manual Loyalty Wizard "


	partner_ids = fields.Many2many('res.partner','m2m_pi_ml','pi_id','ml_id',string='Customer Name')
	loyalty_points = fields.Float(string='Loyalty Points')

	def button_submit(self):
		for partner in self.partner_ids:
			vals = {
				'partner_id':partner.id,
				'points':self.loyalty_points,
				'state' : 'done',
				'transaction_type' : 'credit'
			}
			self.env['all.loyalty.history'].create(vals)
