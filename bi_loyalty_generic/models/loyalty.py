# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError,Warning
import logging
import math
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Integer(string='Loyalty Points',compute='_compute_loyalty_points',store=True)
    loyalty_amount = fields.Float('Loyalty Amount')
    loyalty_history_ids = fields.One2many('all.loyalty.history','partner_id',string='Loyalty history')
    loyalty_deactivate  =  fields.Boolean('Loyalty Deactive')
    tier_id = fields.Many2one('loyalty.tier.config',string='Loyalty Tier')
    total_sales = fields.Float(string='Total Sales',compute= 'update_total_sale')
    ribbon_color = fields.Char('Ribbon Color',related='tier_id.ribbon_color', store=True)
    ribbon_text = fields.Char('Ribbon Text',related='tier_id.ribbon_text', store=True)
    red  =  fields.Boolean('Red',compute= 'compute_red')
    orange  =  fields.Boolean('orange',compute= 'compute_orange')
    yellow  =  fields.Boolean('yellow',compute= 'compute_yellow')
    sky  =  fields.Boolean('sky',compute= 'compute_sky')
    purple  =  fields.Boolean('purple',compute= 'compute_purple')
    pink  =  fields.Boolean('pink',compute= 'compute_pink')
    medium_blue  =  fields.Boolean('medium blue',compute= 'compute_medium_blue')
    blue  =  fields.Boolean('blue',compute= 'compute_blue')
    fushia  =  fields.Boolean('fushia',compute= 'compute_fushia')
    green  =  fields.Boolean('green',compute= 'compute_green')
    light_purple  =  fields.Boolean('light purple',compute= 'compute_light_purple')

    def compute_red(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 1:
                    is_set = True
        self.write({'red':is_set})

    def compute_orange(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 2:
                    is_set = True
        self.write({'orange':is_set})

    def compute_yellow(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 3:
                    is_set = True
        self.write({'yellow':is_set})

    def compute_sky(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 4:
                    is_set = True
        self.write({'sky':is_set})

    def compute_purple(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 5:
                    is_set = True
        self.write({'purple':is_set})

    def compute_pink(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 6:
                    is_set = True
        self.write({'pink':is_set})

    def compute_medium_blue(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 7:
                    is_set = True
        self.write({'medium_blue':is_set})

    def compute_blue(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 8:
                    is_set = True
        self.write({'blue':is_set})

    def compute_fushia(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 9:
                    is_set = True
        self.write({'fushia':is_set})

    def compute_green(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 10:
                    is_set = True
        self.write({'green':is_set})

    def compute_light_purple(self):
        is_set = False
        if self.tier_id:
            if self.ribbon_color and self.ribbon_text:
                if self.ribbon_color == 11:
                    is_set = True
        self.write({'light_purple':is_set})


    def update_total_sale(self):
        for record in self:
            sale_id = self.env['sale.order'].search([('partner_id','=', record.id)])
            pos_id = self.env['pos.order'].search([('partner_id','=', record.id)])
            total_sale = 0
            if sale_id:
                total_sale += sum(order.amount_total for order in sale_id)
            if pos_id:
                total_sale += sum(order.amount_total for order in pos_id)
            record.total_sales = total_sale
    
    @api.model
    def create(self, vals):
        result = super(res_partner, self).create(vals)
        tier_id = self.env['loyalty.tier.config'].search([('default','=',True)],limit=1)
        if tier_id:
            result.write({'tier_id':tier_id.id})
        if self.env.user.company_id.sign_up_bonus:
            vals = {
                'partner_id':result.id,
                'points':self.env.user.company_id.sign_up_bonus,
                'state' : 'done',
                'transaction_type' : 'credit'
            }
            self.env['all.loyalty.history'].create(vals)
        return result
    

    @api.depends('loyalty_history_ids','loyalty_history_ids.state','loyalty_history_ids.points','loyalty_history_ids.transaction_type')
    def _compute_loyalty_points(self):
        for rec in self:
            rec.loyalty_points = 0
            for history in rec.loyalty_history_ids :
                if history.state == 'done' and  history.transaction_type == 'credit' :
                    rec.loyalty_points += history.points
                if history.state == 'done' and  history.transaction_type == 'debit' :
                    rec.loyalty_points -= history.points

    def action_view_loyalty_points(self):
        self.ensure_one()

        partner_loyalty_ids = self.env['all.loyalty.history'].search([('partner_id','=',self.id)])

        return {
            'name': 'Loyalty Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'all.loyalty.history',
            'domain': [('partner_id', '=', self.id)],
        }
    
class all_loyalty_setting(models.Model):
    _name = 'all.loyalty.setting'
    _description = 'all loyalty setting'
        
    name  = fields.Char('Name' ,default='Configuration for Loyalty Management')
    product_id  = fields.Many2one('product.product','Product', domain = [('type', '=', 'service'),('available_in_pos','=',True)],required=True)
    issue_date  =  fields.Date(default=fields.date.today(),required=True)
    expiry_date  = fields.Date('Expiry date',required=True)
    loyalty_basis_on = fields.Selection([('amount', 'Purchase Amount'), ('loyalty_category', 'Product Categories')], string='Loyalty Basis On',required=True)
    active  =  fields.Boolean('Active')
    loyality_amount = fields.Integer('Amount')
    amount_footer = fields.Integer('Footer Amount', related='loyality_amount')
    redeem_ids = fields.One2many('all.redeem.rule', 'loyality_id', 'Redemption Rule')
    loyalty_tier = fields.Many2one('loyalty.tier.config','Loyalty Tier')
    max_range = fields.Integer('Max Range', related='loyalty_tier.max_range')
    min_range = fields.Integer('Min Range', related='loyalty_tier.min_range')

    @api.model
    def create(self, vals):
        result = super(all_loyalty_setting, self).create(vals)
        today_date = datetime.today().date() 
        if result.loyalty_tier:
            config = self.env['all.loyalty.setting'].sudo().search([('active','=',True),('loyalty_tier', '=', result.loyalty_tier.id )])
            if len(config)>1:
                msg = _("You can not apply same tier in two Loyalty Configuration!")
                raise ValidationError(msg)

        return result

    @api.model
    def search_loyalty_product(self,product_id):
        
        product = self.product_id.search([('id','=',product_id)])
        return product.id




class web_redeem_rule(models.Model):
    _name = 'all.redeem.rule' 
    _description = 'all redeem rule'   
    
    name = fields.Char('Name' ,default='Configuration for Website Redemption Management')
    min_amt = fields.Integer('Minimum Points')
    max_amt = fields.Integer('Maximum Points')
    reward_amt = fields.Integer('Redemption Amount')
    loyality_id = fields.Many2one('all.loyalty.setting', 'Loyalty ID')
    points_redeem = fields.Integer('Points Redeem')

    @api.onchange('max_amt','min_amt')
    def _check_amt(self):
        if (self.max_amt !=0):
            if(self.min_amt > self.max_amt):
                msg = _("Minimum Point is not larger than Maximum Point")
                raise ValidationError(msg)
        return

    @api.onchange('reward_amt')
    def _check_reward_amt(self):
        if self.reward_amt !=0:
            if self.reward_amt <= 0:            
                msg = _("Reward amount is not a zero or less than zero")
                raise ValidationError(msg)
        return

    @api.constrains('min_amt','max_amt')
    def _check_points(self):
        for line in self:
            record = self.env['all.redeem.rule'].search([('loyality_id','=',line.loyality_id.id)])
            for rec in record :
                if line.id != rec.id:
                    if (rec.min_amt <= line.min_amt  <= rec.max_amt) or (rec.min_amt <=line.max_amt  <= rec.max_amt):
                        msg = _("You can not create Redemption Rule with same points range.")
                        raise ValidationError(msg)
                        return


class web_loyalty_history(models.Model):
    _name = 'all.loyalty.history'
    _rec_name = 'partner_id'
    _order = 'id desc'
    _description = 'all loyalty history'  

    def _compute_check_state(self):
        for rec in self:
            rec.check_state = False
            if not rec.state :
                if rec.order_id and rec.order_id.state in ['sale','done'] :
                    rec.state = 'done'
                elif rec.pos_order_id :
                    rec.state = 'done'
                else:
                    rec.state = 'draft' 
        
    order_id  = fields.Many2one('sale.order','Sale Order')
    pos_order_id  = fields.Many2one('pos.order','POS Order')
    partner_id  = fields.Many2one('res.partner','Customer')
    date  =  fields.Datetime(default = datetime.now())
    generated_from = fields.Selection([('sale', 'Sale'), ('pos', 'POS'),('website','Website')], string='Generated From')
    transaction_type = fields.Selection([('credit', 'Credit'), ('debit', 'Debit')], string='Transaction Type')
    points = fields.Integer('Loyalty Points')
    amount = fields.Char('Amount')
    currency_id = fields.Many2one('res.currency', 'Currency')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, required=True)
    loyality_id = fields.Many2one('all.loyalty.setting', 'Loyalty ID')
    check_state = fields.Boolean(compute='_compute_check_state')
    state = fields.Selection([('draft','Draft'),('done','Confirmed'),
        ('cancel','Cancelled')],string="State",default='draft',readonly=True, copy=False)
    credit_value = fields.Float('Credit Value', compute='_compute_credit_value')

    def _compute_credit_value(self):
        credit_value = 0
        today_date = datetime.today().date() 
        for record in self:
            if record.partner_id.tier_id:
                config = self.env['all.loyalty.setting'].sudo().search([('active','=',True),('issue_date', '<=', today_date ),
                                ('expiry_date', '>=', today_date ),('loyalty_tier', '=', record.partner_id.tier_id.id )],limit=1)
                if config:
                    for rule in config.redeem_ids:
                        if rule.min_amt <= record.points and record.points <= rule.max_amt :
                            credit_value = record.points * (rule.reward_amt /rule.points_redeem)

            record.write({'credit_value':credit_value})
        
class loyalty_tier_configuration(models.Model):
    _name = 'loyalty.tier.config'
    _description = 'Loyalty Tier Configuration'
    _rec_name = 'tier_name'

    tier_name = fields.Char('Name')
    min_range = fields.Integer('Minimum Range')
    max_range = fields.Integer('Maximum Range')
    default = fields.Boolean('Default')
    ribbon_color = fields.Char('Ribbon Color')
    ribbon_text = fields.Char('Ribbon Text')

    @api.onchange('default')
    def _check_default_box(self):
        tier_id = self.search([('default', '=', self.default)])
        for rec in tier_id:
            if rec.default == True:
                raise ValidationError("Default tier used only for one user")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
