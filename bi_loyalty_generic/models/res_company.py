# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"


    product_ids = fields.Many2many('product.product','product_id' ,string='Product')
