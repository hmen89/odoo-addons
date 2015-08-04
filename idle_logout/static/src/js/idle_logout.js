openerp.idle_logout = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.idle_logout = {};



    instance.web.WebClient.include({
        show_application: function () {
            var self = this;
            return $.when(this._super.apply(this, arguments)).then(
                function(){
                    var res_users = new instance.web.Model('res.users');
                    res_users.call('read', [[self.session.uid], ['idle_timer']]).then(function(reg_seconds) {
                        //Define default
                        var seconds = 0;
                        if(reg_seconds.length>0){
                            seconds = reg_seconds[0]['idle_timer'];
                        }

                        if (seconds<=0){
                            seconds =  900; //15 minutes
                        }
                        self.session.docTimeout = seconds*1000;
                        $(document).idleTimer({ timeout: self.session.docTimeout });
                        $(document).on("idle.idleTimer", function (event, elem, obj) {
                            instance.webclient.has_uncommitted_changes = function(){
                                return false;
                            };
                            instance.webclient.on_logout();
                        });
                        /*$(document).on("active.idleTimer", function (event, elem, obj, e) {
                            console.log('Active');
                        });*/
                    }).fail(function(result, ev){
                        ev.preventDefault();
                    });
                }
            );
        },
    });


    instance.web.form.FieldTextHtml = instance.web.form.FieldTextHtml.extend({
        initialize_content: function(){
            console.log('initialize');
            this._super.apply(this, arguments);
            var docTimeout = this.session.docTimeout;
            var self = this;
            var odoo_document = $(document);
            if (! this.get("effective_readonly")) {
                //Define default

                /*var cleditor_body = this.$cleditor.doc.body;
                $(cleditor_body).idleTimer = function (firstParam) {
                    if (this[0]) {
                        return $.idleTimer(firstParam, this[0]);
                    }

                    return this;
                };
                $(cleditor_body).idleTimer({ timeout: docTimeout });
                $(cleditor_body).on("idle.idleTimer", function (event, elem, obj) {
                    odoo_document.trigger('idle.idleTimer');
                });
                $(cleditor_body).on("active.idleTimer", function (event, elem, obj, e) {
                    odoo_document.trigger('active.idleTimer');
                });
;*/
                self,cleditor_doctimeout = null;
                var cleditor_doc = this.$cleditor.doc;

                $(cleditor_doc).on('mousemove keydown wheel DOMMouseScroll mousewheel mousedown touchstart touchmove MSPointerDown MSPointerMove',function(evt){
                    odoo_document.trigger(evt.type);
                    clearTimeout(self.cleditor_doctimeout);
                    self.cleditor_doctimeout = setTimeout(function() {
                        odoo_document.trigger('idle.idleTimer');
                    }, docTimeout);

                })

            }

        },
        destroy: function(){
            var self = this;
            clearTimeout(self.cleditor_doctimeout);
            self,cleditor_doctimeout = null;
            this._super.apply(this, arguments);
        }
    });


   
};




