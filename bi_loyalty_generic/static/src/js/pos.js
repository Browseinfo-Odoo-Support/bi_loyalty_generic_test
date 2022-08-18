odoo.define('bi_loyalty_generic.pos', function(require) {
	"use strict";

	let models = require('point_of_sale.models');
	let utils = require('web.utils');

	// Load Models
	models.load_models({
		model: 'all.loyalty.setting',
		fields: ['name', 'product_id', 'issue_date', 'expiry_date', 'loyalty_basis_on', 'loyality_amount', 'active','redeem_ids','loyalty_tier','max_range','min_range'],
		domain: function(self) 
		{
			let today = new Date();
			let dd = today.getDate();
			let mm = today.getMonth()+1; //January is 0!

			let yyyy = today.getFullYear();
			if(dd<10){
				dd='0'+dd;
			} 
			if(mm<10){
				mm='0'+mm;
			} 
			today = yyyy+'-'+mm+'-'+dd;
			return [['issue_date', '<=',today],['expiry_date', '>=',today],['active','=',true]];
		},
		loaded: function(self, pos_loyalty_setting) {
			self.pos_loyalty_setting = pos_loyalty_setting;
		},
	});

	models.load_models({
		model: 'all.redeem.rule',
		fields: ['reward_amt','min_amt','max_amt','loyality_id','points_redeem'],
		loaded: function(self, pos_redeem_rule) {
			self.pos_redeem_rule = pos_redeem_rule;
		},
	});
	
	models.load_fields('pos.category', ['Minimum_amount']);
	models.load_fields('res.partner', ['loyalty_points','loyalty_amount','loyalty_deactivate','total_sales']);
	models.load_fields('loyalty.tier.config', ['max_range','min_range']);
		
	
	let OrderSuper = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			OrderSuper.initialize.apply(this, arguments);
			let self = this;
			this.loyalty = this.loyalty  || 0;
			this.redeemed_points = this.redeemed_points || 0;
			this.redeem_done = this.redeem_done || false;
			// setInterval(function(){ 
			// 	self.pos.load_new_partners();
			// }, 10000);
		},
		
		remove_orderline: function(line) {
			this.redeem_done = false;
			if(line.id ==this.get('remove_line'))
			{
				this.set('remove_true', true);
				let partner = this.get_client();
				if (partner) {
					partner.loyalty_points = parseInt(partner.loyalty_points) + parseInt(this.get('redeem_point')) ;
				}
			}
			else
			{
				this.set('remove_true', false);
			}
			OrderSuper.remove_orderline.apply(this, arguments);
		},

		get_redeemed_points: function() {
			return parseInt(this.redeemed_points);
		},

		get_loyalty_rule: function() {
			let round_pr = utils.round_precision;
			let round_di = utils.round_decimals;
			let rounding = this.pos.currency.rounding;
			let final_loyalty = 0
			let order = this.pos.get_order();
			let orderlines = this.get_orderlines();
			let partner_id = this.get_client();
			let redeem_rule = this.pos.pos_redeem_rule;

			if(this.pos.pos_loyalty_setting.length != 0)
			{	
				var increment = 0;
				var rule_increment = 0;
				for (var pos_loyalty_set in this.pos.pos_loyalty_setting) {
					if (partner_id){
						if (! partner_id.loyalty_deactivate){
							if (partner_id.total_sales >= this.pos.pos_loyalty_setting[increment].min_range && partner_id.total_sales <= this.pos.pos_loyalty_setting[increment].max_range){
							    for (var rule in redeem_rule) {
							    	if (this.pos.pos_loyalty_setting[increment].id <= redeem_rule[rule_increment].loyality_id[0]){
								    	if (redeem_rule[rule_increment].min_amt <= partner_id.loyalty_points  &&   partner_id.loyalty_points <= redeem_rule[rule_increment].max_amt) {
								    		var loyalty_rule = redeem_rule[rule_increment]
								    	}
								    	
								    }
							    	rule_increment = rule_increment+1
							    }
							}
						}
					}
				increment = increment+1
				}
			}
			return loyalty_rule;
		},

		get_loyalty_amount: function() {
			let round_pr = utils.round_precision;
			let round_di = utils.round_decimals;
			let rounding = this.pos.currency.rounding;
			let final_loyalty = 0
			let order = this.pos.get_order();
			let orderlines = this.get_orderlines();
			let partner_id = this.get_client();
			let redeem_rule = this.pos.pos_redeem_rule;

			if(this.pos.pos_loyalty_setting.length != 0)
			{	
				var increment = 0;
				var rule_increment = 0;
				for (var pos_loyalty_set in this.pos.pos_loyalty_setting) {
					if (partner_id){
						if (! partner_id.loyalty_deactivate){
							if (partner_id.total_sales >= this.pos.pos_loyalty_setting[increment].min_range && partner_id.total_sales <= this.pos.pos_loyalty_setting[increment].max_range){
							    for (var rule in redeem_rule) {
							    	if (this.pos.pos_loyalty_setting[increment].id <= redeem_rule[rule_increment].loyality_id[0]){
								    	if (redeem_rule[rule_increment].min_amt <= partner_id.loyalty_points && partner_id.loyalty_points <= redeem_rule[rule_increment].max_amt){
								    		var loyalty_amount = (partner_id.loyalty_points/ (redeem_rule[rule_increment].points_redeem))
								    	}
								    }
							    	rule_increment = rule_increment+1
							    }
							}
						}
					}
				increment = increment+1
				}
			}
			if(loyalty_amount){
				return loyalty_amount.toFixed(2);
			}
			else{
				return 0.0
			}
		},

		get_total_loyalty: function() {
			let round_pr = utils.round_precision;
			let round_di = utils.round_decimals;
			let rounding = this.pos.currency.rounding;
			let final_loyalty = 0
			let order = this.pos.get_order();
			let orderlines = this.get_orderlines();
			let partner_id = this.get_client();

			if(this.pos.pos_loyalty_setting.length != 0)
			{	
				var increment = 0;
				for (var pos_loyalty_set in this.pos.pos_loyalty_setting) {
					if (partner_id){
						if (! partner_id.loyalty_deactivate){
							if (partner_id.total_sales >= this.pos.pos_loyalty_setting[increment].min_range && partner_id.total_sales <= this.pos.pos_loyalty_setting[increment].max_range){
							    if (this.pos.pos_loyalty_setting[increment].loyalty_basis_on == 'loyalty_category') {
									if (partner_id)
									{
										let loyalty = 0
										for (let i = 0; i < orderlines.length; i++) {
											let lines = orderlines[i];
											let cat_ids = this.pos.db.get_category_by_id(lines.product.pos_categ_id[0])
											if(cat_ids){
												if (cat_ids['Minimum_amount']>0)
												{
													final_loyalty += parseInt(lines.get_price_with_tax() / cat_ids['Minimum_amount']);
												}
											}
										}
									}
							   }else if (this.pos.pos_loyalty_setting[increment].loyalty_basis_on == 'amount') {
									let loyalty_total = 0
									if (order && partner_id)
									{
										let amount_total = order.get_total_with_tax();
										let subtotal = order.get_total_without_tax();
										let loyaly_points = this.pos.pos_loyalty_setting[increment].loyality_amount;
										final_loyalty += (amount_total / loyaly_points);
										loyalty_total = order.get_client().loyalty_points + final_loyalty;
									}
								}
							}
						}
					}
				increment = increment+1
				}
			}
			return Math.floor(final_loyalty);
		},

		export_as_JSON: function() {
			let json = OrderSuper.export_as_JSON.apply(this, arguments);
			json.redeemed_points = parseInt(this.redeemed_points);
			json.loyalty = this.get_total_loyalty();
			json.redeem_done = this.redeem_done;
			return json;
		},

		init_from_JSON: function(json){
			OrderSuper.init_from_JSON.apply(this,arguments);
			this.loyalty = json.loyalty;
			this.redeem_done = json.redeem_done;
			this.redeemed_points = json.redeemed_points;
		},
	
	});

});
