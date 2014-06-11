/* Loads the Image into a modal dialog.
 *
 * Examples
 *
 *   <a data-module="modal-image"">Image</a>
 *
 */
this.ckan.module('modal-contact', function (jQuery, _) {
  return {

    /* holds the loaded lightbox */
    modal: null,

    options: {
      imageUrl: null,
      form: '/api/1/util/snippet/contact_form.html'
    },

    /* Sets up event listeners
     *
     * Returns nothing.
     */
    initialize: function () {
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

      this.loadForm().done(function (html) {

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
                        module.flash_success('Thank you for your request - we will answer you as soon as possible.');
                    } else if (!jQuery.isEmptyObject(results.errors)){
                        module.processFormError(form, results.errors)
                    }else{
                        // If not success and there's no user input errors, the email submission has failed
                        module.hide();
                        module.flash_error('Sorry, there was an error sending the email. Please try again later.');
                    }
                }
              });

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

    loadForm: function () {
      if (!this.promise) {
        this.loading();

        // This should use sandbox.client!
        this.promise = jQuery.get(this.options.form);
        this.promise.then(this._onFormSuccess, this._onFormError);
      }
      return this.promise;
    },

    /* Event handler for clicking on the element */
    _onClick: function (event) {
      event.preventDefault();
      this.show();
    },

    /* Success handler for when the template is loaded */
    _onFormSuccess: function () {
      this.loading(false);
    },

    /* error handler when the template fails to load */
    _onFormError: function () {
      this.loading(false);
      this.sandbox.notify(this.i18n('loadError'));
    }

  };
});