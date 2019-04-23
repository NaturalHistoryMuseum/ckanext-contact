ckan.module('recaptcha-contact', function($, _) {
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
                const googleURL = 'https://www.google.com/recaptcha/api.js?render=' + self.key;
                $.getScript(googleURL, function() {
                    grecaptcha.ready(function() {
                        self.form.on('submit.recaptcha_contact', self.onSubmit);
                    });
                });
            }
        },

        /**
         * Called when the form is submitted.
         */
        onSubmit: function(event) {
            // stop the form going through
            event.preventDefault();
            // start the async call to Google to get a recaptcha token
            grecaptcha.execute(self.key, {action: self.action}).then(self.onTokenResponse);
        },

        /**
         * Called when we get the token back from Google.
         *
         * @param token the recaptcha token
         */
        onTokenResponse: function(token) {
            // create an input element so that we can pass the token in the form submission
            const input = document.createElement('input');
            input.setAttribute('type', 'hidden');
            input.setAttribute('name','g-recaptcha-response');
            input.setAttribute('value', token);
            // add the input to the form
            self.form.prepend(input);
            // need to remove our listener otherwise we create an infinite submit loop
            self.form.off('submit.recaptcha_contact');
            // submit the form as normal
            self.form.submit();
        }
    };
});
