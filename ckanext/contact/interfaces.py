import ckan.plugins.interfaces as interfaces


class IContact(interfaces.Interface):
    """
    Hook into contact form
    """
    def mail_alter(self, mail_dict, data_dict):
        """
        Allow altering of email values
        For example, allow directing contact form dependent on form values

        @param data_dict: form values
        @param mail_dict: dictionary of mail values, used in mailer.mail_recipient
        @return: altered mail_dict
        """
        return mail_dict