/* Loads the Image into a modal dialog.
 *
 * Examples
 *
 *   <a data-module="modal-image"">Image</a>
 *
 */
this.ckan.module('modal-contact', function (jQuery, _) {
  var self
  return {

    /* holds the loaded lightbox */
    modal: null,

    options: {
      template: '/api/1/util/snippet/contact_form.html',
      i18n: {
        noTemplate: _('Sorry, we could not load the contact form. Please try again later.'),
        loadError: _('Sorry, we could not load the contact form. Please try again later.'),
        onSuccess: _('Thank you for contacting us, and we will try and reply as soon as possible.<br />Unfortunately due to the number of enquiries the Museum receives, we cannot always reply in person to every one.'),
        onError: _('Sorry, there was an error sending the email. Please try again later.')
      }
    },

    /* Sets up event listeners
     *
     * Returns nothing.
     */
    initialize: function () {
      self = this;
      jQuery.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },

    /* Loading
     *
     */
    loading: function (loading) {
      this.el.button(loading !== false ? 'loading' : 'reset');
    },

    /* Displays the image
     *
     */
    show: function () {
      var sandbox = this.sandbox,
          module = this;

      this.loadTemplate().done(function (html) {

        module.modal = jQuery(html);
        module.modal.find('.modal-header :header').append('<button class="close" data-dismiss="modal">×</button>');
        module.modal.find('form').submit(function(event){

            event.preventDefault();
            var form = $(this);

            jQuery.ajax({
                url: '/contact/ajax',
                type: this.method,
                data: form.serialize(),
                success: function (results) {
                    if (results.data['success'] !== undefined){
                        module.hide();
                        self.flash_success(self.i18n('onSuccess'))
                    } else if (!jQuery.isEmptyObject(results.errors)){
                        self.processFormError(form, results.errors)
                    }else{
                        // If not success and there's no user input errors, the email submission has failed
                        module.hide();
                        self.flash_error(self.i18n('onError'));
                    }
                }
              });

            // TODO: Add cancel button

        });

        module.modal.modal().appendTo(sandbox.body);

      });

    },

    /* Process errors returned from form submission process
     *
     */
    processFormError: function (form, errors) {
        // Remove all errors & classes
        form.find('.error-block').remove();
        form.find('.error').removeClass('error');

        // Lop through all the errors, adding the error message and error classes
        for (var k in errors){
            var controls = form.find("[name='" + k + "']").parent('.controls');
            controls.append('<span class="error-block">' + errors[k] + '</span>');
            controls.parent('.control-group').addClass('error');
        }
    },

    /* Hides the modal.
     *
     */
    hide: function () {
      if (this.modal) {
        this.modal.modal('hide');
      }
    },

    flash_error: function (message) {
        this.flash(message, 'alert-error')
    },

    flash_success: function (message) {
        this.flash(message, 'alert-success')
    },

    flash: function (message, category) {
        $('.flash-messages').append('<div class="alert ' + category + '">' + message + '</div>');
    },

    loadTemplate: function () {

      if (!this.options.template) {
        this.sandbox.notify(this.i18n('noTemplate'));
        return jQuery.Deferred().reject().promise();
      }

      if (!this.promise) {
        this.loading();

        // This should use sandbox.client!
        this.promise = jQuery.get(this.options.template);
        this.promise.then(this._onTemplateSuccess, this._onTemplateError);
      }
      return this.promise;
    },

    /* Event handler for clicking on the element */
    _onClick: function (event) {
      event.preventDefault();
      this.show();
    },

    /* Success handler for when the template is loaded */
    _onTemplateSuccess: function () {
      this.loading(false);
    },

    /* error handler when the template fails to load */
    _onTemplateError: function () {
      this.loading(false);
      this.sandbox.notify(this.i18n('loadError'));
    }

  };
});