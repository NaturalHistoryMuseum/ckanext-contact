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
                    if (jQuery.isEmptyObject(results.errors)){
                        module.hide()
                    }else{
                        module.processError(form, results.errors)
                    }

                }
              });

        });

        module.modal.modal().appendTo(sandbox.body);

      });

    },

    /* Hides the modal.
     *
     */
    processError: function (form, errors) {
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
