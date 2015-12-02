// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.

;(function () {

window.GroupDetailsView = Backbone.View.extend({
    initialize: function () {
        this.render();
    },
    render: function () {
      new GroupPageHeaderView({model: this.model}).$el
          .appendTo(this.$el);
      new GroupRootPasswordView({model: this.model}).$el
          .appendTo(this.$el);
    },
});

window.GroupPageHeaderView = Backbone.View.extend({
    template: JST['group-page-header'],
    initialize: function () {
        this.listenTo(this.model, 'change:display_name change:can_edit', this.render);
        this.render();
    },
    events: {
        'click .edit': 'edit',
        'click .delete': 'delete',
    },
    render: function () {
      this.$el.html(this.template(this.model.attributes));
    },
    edit: function () {
        new GroupEditModal({model: this.model});
    },
    'delete': function () {
        var model = this.model, $del_btn = this.$('button.delete');
        $del_btn.button('loading');
        bootbox.confirm_as_promise('<p>Are you sure you want to delete this group?</p>')
            .fail(function () { $del_btn.button('reset'); })
            .then(function () { return model.destroy(); })
            .fail(_.bind(this.delete_error, this))
            .done(function () { window.location = beaker_url_prefix + 'groups/'; });
    },
    delete_error: function(xhr) {
        if (!_.isEmpty(xhr)) {
            $.bootstrapGrowl('<h4>Failed to delete</h4> ' +
                  xhr.statusText + ': ' + xhr.responseText,
                    {type: 'error'});
            this.$('button.delete').button('reset');
        }
    },
});

window.GroupRootPasswordView = Backbone.View.extend({
    id: 'root_pw_display',
    template: JST['group-rootpassword'],
    initialize: function () {
        this.listenTo(this.model, 'change:root_password change:can_view_rootpassword', this.render);
        this.render();
    },
    render: function function_name() {
      this.$el.html(this.template(this.model.attributes));
    },
});

var GroupEditModal = Backbone.View.extend({
    tagName: 'div',
    className: 'modal',
    template: JST['group-edit'],
    events: {
        'submit form': 'submit',
        'hidden': 'remove',
    },
    initialize: function () {
        this.render();
        this.$el.modal();
        this.$('[name=group_name]').focus();
    },
    render: function () {
        this.$el.html(this.template(this.model.attributes));
        var model = this.model;
        this.$('input, select').each(function (i, elem) {
            $(elem).val(model.get(elem.name));
        });
        this.$('select').selectpicker();
    },
    submit: function (evt) {
        evt.preventDefault();
        this.$('.sync-status').empty();
        this.$('.modal-footer button').button('loading');
        var attributes = _.object(_.map(this.$('input, select'),
                function (elem) { return [elem.name, $(elem).val()]; }));
        this.model.save(attributes,
            {patch: true, wait: true})
            .done(_.bind(this.save_success, this))
            .fail(_.bind(this.save_error, this));
    },
    save_success: function (response, status, xhr) {
        if (xhr.getResponseHeader('Location'))
            window.location = xhr.getResponseHeader('Location');
        else
            this.$el.modal('hide');
    },
    save_error: function (xhr) {
        $('<div class="alert alert-error"/>')
            .text(xhr.statusText + ': ' + xhr.responseText)
            .appendTo(this.$('.sync-status'));
        this.$('.modal-footer button').button('reset');
    },
});

})();
