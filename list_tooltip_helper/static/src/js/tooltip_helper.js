openerp.list_tooltip_helper = function(instance){

    //var module = instance.point_of_sale;
    var _t = instance.web._t,
    _lt = instance.web._lt;

    var QWeb = instance.web.qweb;

    instance.web.ListView.include({

        compute_aggregates: function (records) {
            var self = this;
            this._super(records);

            var tooltips = this.$el.find("table.oe_list_content").find("td.oe_list_field_cell").tooltip({
                position: {
                    my: "left top",
                    at: "right+5 top-5"
                }
            });

        },

    });

}