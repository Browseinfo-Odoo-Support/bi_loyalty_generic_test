odoo.define('bi_loyalty_generic.ClientListScreen', function(require) {
	'use strict';

	const ClientListScreen = require('point_of_sale.ClientListScreen');
	const Registries = require('point_of_sale.Registries');
	const core = require('web.core');
	const _t = core._t;

	const NewClientListScreen = ClientListScreen => class extends ClientListScreen {
		constructor() {
			super(...arguments);
			// this.update_customers();
			var self = this;
			setInterval(function(){
				self.searchClient();
			}, 5000);
			this.searchClient()
		}
		
		// async update_customers() {
		// 	await this.env.pos.load_new_partners();
		// }

		async searchClient() {
            let result = await this.getNewClient();
            this.env.pos.db.add_partners(result);
            this.render();
        }

		async getNewClient() {
            var domain = [];
            if(this.state.query) {
                domain = [["name", "ilike", this.state.query + "%"]];
            }
            var fields = _.find(this.env.pos.models, function(model){ return model.label === 'load_partners'; }).fields;
            var result = await this.rpc({
                model: 'res.partner',
                method: 'search_read',
                args: [domain, fields],
                kwargs: {
                    limit: 10,
                },
            },{
                timeout: 3000,
                shadow: true,
            });

            return result;
        }
	};

	Registries.Component.extend(ClientListScreen, NewClientListScreen);

	return ClientListScreen;

});