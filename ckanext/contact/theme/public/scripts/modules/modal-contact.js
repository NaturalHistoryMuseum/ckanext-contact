/*
 * Modal contact form, triggered from the a tag the module is loaded onto. Uses ajax to post the
 * message to the server.
 *
 * Example:
 *
 *   <a data-module="modal-contact">Contact</a>
 *
 */
ckan.module('modal-contact', function($, _) {
    let self;

    return {
        /**
         * Initialises the module by setting up the recaptcha if necessary and setting up event
         * listeners.
         */
        initialize: function() {
            self = this;
            self.modal = null;
            self.messages = {
                'onSuccess': _('Thank you for contacting us, and we will try and reply as soon as possible.<br />Unfortunately due to the number of enquiries the Museum receives, we cannot always reply in person to every one.'),
                'onError': _('Sorry, there was an error sending the email. Please try again later.')
            };
            // define the template if it is not passed
            self.options.template = self.options.template || 'contact_form.html';
            self.el.on('click', self._onClick);
        },

        /**
         * Loads and displays the contact form modal.
         */
        show: function() {
            self.sandbox.client.getTemplate('contact_form.html', self.options, function(html) {
                // initialise the recaptcha context. By doing this here in the show function we
                // avoid showing the recaptcha badge on the page before the user has even given an
                // indication that they want to contact us which avoids confusion
                if (self.options.key) {
                    self.context = window.contacts_recaptcha.load(self.options.key, self.options.action);
                }
                self.modal = $(html);
                self.modal.find('.modal-header :header').append('<button class="close" data-dismiss="modal">×</button>');
                self.modal.find('form').submit(function(event) {
                    event.preventDefault();

                    let form = self.modal.find('form');

                    if (self.context) {
                        self.context.addToken(form).then(function(token) {
                            self.sendForm(form);
                        });
                    } else {
                        self.sendForm(form);
                    }

                    // TODO: Add cancel button
                });

                self.modal.modal().appendTo(self.sandbox.body);
            });

        },

        sendForm: function(form) {
            $.ajax({
                url: '/contact/ajax',
                type: self.method,
                data: form.serialize(),
                success: function(results) {
                    if (results.success) {
                        self.hide();
                        self.flash_success(self.i18n(self.messages.onSuccess))
                    } else if (!$.isEmptyObject(results.errors)) {
                        self.processFormError(form, results.errors)
                    } else if (!!results.recaptcha_error) {
                        self.hide();
                        self.flash_error(results.recaptcha_error);
                    } else {
                        // if not success and there's no user input errors, the email
                        // submission has failed
                        self.hide();
                        self.flash_error(self.i18n(self.messages.onError));
                    }
                }
            });
        },

        /**
         * Process errors returned from form submission process.
         */
        processFormError: function(form, errors) {
            // remove all errors & classes
            form.find('.error-block').remove();
            form.find('.error').removeClass('error');

            // loop through all the errors, adding the error message and error classes
            for (let k in errors) {
                let controls = form.find("[name='" + k + "']").parent('.controls');
                controls.append('<span class="error-block">' + errors[k] + '</span>');
                controls.parent('.control-group').addClass('error');
            }
        },

        /**
         * Hides the modal.
         */
        hide: function() {
            if (self.modal) {
                self.modal.modal('hide');
            }
        },

        flash_error: function(message) {
            self.flash(message, 'alert-error')
        },

        flash_success: function(message) {
            self.flash(message, 'alert-success')
        },

        flash: function(message, category) {
            $('.flash-messages').append('<div class="alert ' + category + '">' + message + '</div>');
        },

        /**
         * Event handler for clicking on the element.
         *
         * @private
         */
        _onClick: function(event) {
            event.preventDefault();
            self.show();
        },
    };
});