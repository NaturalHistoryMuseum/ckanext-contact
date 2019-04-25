/*
 * Non-modal contact form. Should be attached to the form itself. The data is sent as a standard
 * POST form submit.
 *
 * Example:
 *
 *   <form data-module="form-contact"> ... </form>
 *
 */
ckan.module('form-contact', function($, _) {
    let self = null;

    return {
        /**
         * Initialisation function for this module, just sets up some variables and sets up the
         * event listeners once the recaptcha library is ready.
         */
        initialize: function() {
            self = this;
            self.form = this.el;
            self.key = this.options.key;
            self.action = this.options.action;

            if (self.key) {
                // setup the recaptcha context
                self.context = window.contacts_recaptcha.load(self.key, self.action);
                // add a callback on the form's submission
                self.form.on('submit', self.onSubmit);
            }
        },

        /**
         * Called when the form is submitted.
         */
        onSubmit: function(event) {
            // stop the form going through
            event.preventDefault();

            // add the token to the form and then submit it when ready
            self.context.addToken(self.form).then(function(token) {
                // remove the listener we added so that we don't create an infinite loop
                self.form.off('submit', self.onSubmit);
                // submit the form as normal
                self.form.submit();
            });
        },
    };
});
