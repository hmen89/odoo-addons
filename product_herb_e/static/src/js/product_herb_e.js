odoo.define('product_herb_e.product_herb_e', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var utils = require('web.utils');
var round_pr = utils.round_precision;

//models.load_fields("pos.category", "on_screen");

/*We are replacing the domain when we find the model.*/
$.each(models.PosModel.prototype.models,function(i,model) {
    console.log(model);
    if (model.model=='pos.category'){
        model.domain = [['on_screen','=',true]];
    }
});

models.load_models({
        model:  'product.product',
        fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
                 'to_weight', 'uom_id', 'description_sale', 'description', 'sort_code',
                 'product_tmpl_id'],
        order:  ['sort_code','sequence','name',],
        domain: [['sale_ok','=',true],['available_in_pos','=',true]],
        context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
        loaded: function(self, products){

            self.db.product_by_category_id = [];
            self.db.stored_categories = self.db.product_by_category_id;

            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                var search_string = self.db._product_search_string(product);
                var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : self.db.root_category_id;
                product.product_tmpl_id = product.product_tmpl_id[0];
                if(!self.db.stored_categories[categ_id]){
                    self.db.stored_categories[categ_id] = [];
                }
                self.db.stored_categories[categ_id].push(product.id);

                if(self.db.category_search_string[categ_id] === undefined){
                    self.db.category_search_string[categ_id] = '';
                }
                self.db.category_search_string[categ_id] += search_string;

                self.db.product_by_id[product.id] = product;
                if(product.barcode){
                    self.db.product_by_barcode[product.barcode] = product;
                }
            }
        },
    });

var ScaleScreenWidget = screens.ScaleScreenWidget.include({
    get_product_weight_string: function(){
        var product = this.get_product();
        var defaultstr = (this.weight || 0).toFixed(3) + ' g';
        if(!product || !this.pos){
            return defaultstr;
        }
        var unit_id = product.uom_id;
        if(!unit_id){
            return defaultstr;
        }
        var unit = this.pos.units_by_id[unit_id[0]];
        var weight = round_pr(this.weight || 0, unit.rounding);
        var weightstr = weight.toFixed(Math.ceil(Math.log(1.0/unit.rounding) / Math.log(10) ));
            weightstr += ' g';
        return weightstr;
    },
});



});


