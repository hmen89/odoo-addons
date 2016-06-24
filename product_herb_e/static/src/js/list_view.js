odoo.define('product_herb_e.ListHerbE', function (require) {
    "use strict";
    /*---------------------------------------------------------
     * Odoo Herb-e List view
     *---------------------------------------------------------*/
    /**
     * handles editability case for lists, because it depends on form and forms already depends on lists it had to be split out
     * @namespace
     */
    var core = require('web.core')
    var ListView = require('web.ListView');
    var FormView = require('web.FormView');
    var KanbanView = require('web_kanban.KanbanView');

    var _t = core._t;

    ListView.include(/** @lends instance.web.ListView# */{

        /**
         * Extend the render_buttons function of ListView by adding event listeners
         * in the case of an editable list.
         * @return {jQuery} the rendered buttons
         */
        render_buttons: function () {
            var self = this;

            this._super.apply(this, arguments); // Sets this.$buttons
            if (this.model=='product.template' || this.model=='product.product'){
                this.$buttons.find('.o_list_button_add').off('click').on('click', function(e){
                    e.preventDefault();
                    self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: 'product.new',
                                views: [[false, 'form']],
                                target: 'new',
                                name: 'Herb-e New Product Wizard'
                            });
                })
                this.$buttons.find('.o_list_button_import').hide();
            }
            /*if (add_button && (this.editable() || this.grouped)) {
                var self = this;
                this.$buttons
                    .off('click', '.o_list_button_save')
                    .on('click', '.o_list_button_save', this.proxy('save_edition'))
                    .off('click', '.o_list_button_discard')
                    .on('click', '.o_list_button_discard', function (e) {
                        e.preventDefault();
                        self.cancel_edition();
                    });
            }*/
        },
    });



    KanbanView.include(/** @lends instance.web.ListView# */{

        /**
         * Extend the render_buttons function of ListView by adding event listeners
         * in the case of an editable list.
         * @return {jQuery} the rendered buttons
         */
        render_buttons: function () {
            var self = this;

            this._super.apply(this, arguments); // Sets this.$buttons
            if (this.model=='product.template' || this.model=='product.product'){
                /*this.$buttons.find('button.o-kanban-button-new').off('click').on('click', function(e){
                    e.preventDefault();
                    self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: 'product.new',
                                views: [[false, 'form']],
                                target: 'new',
                                name: 'Herb-e New Product Wizard'
                            });
                })*/
                this.$buttons.find('button.o-kanban-button-new').hide();
                //this.$buttons.find('.o_list_button_import').hide();
            }
            /*if (add_button && (this.editable() || this.grouped)) {
                var self = this;
                this.$buttons
                    .off('click', '.o_list_button_save')
                    .on('click', '.o_list_button_save', this.proxy('save_edition'))
                    .off('click', '.o_list_button_discard')
                    .on('click', '.o_list_button_discard', function (e) {
                        e.preventDefault();
                        self.cancel_edition();
                    });
            }*/
        },
    });


    FormView.include({
        render_buttons: function ($node) {
            var self = this;

            this._super.apply(this, arguments); // Sets this.$buttons
            if (this.model=='product.template' || this.model=='product.product'){
                this.$buttons.find('.oe_form_button_edit').hide();
                this.$buttons.find('.oe_form_button_create').hide();
            }
            /*if (add_button && (this.editable() || this.grouped)) {
                var self = this;
                this.$buttons
                    .off('click', '.o_list_button_save')
                    .on('click', '.o_list_button_save', this.proxy('save_edition'))
                    .off('click', '.o_list_button_discard')
                    .on('click', '.o_list_button_discard', function (e) {
                        e.preventDefault();
                        self.cancel_edition();
                    });
            }*/
        },
    })


});