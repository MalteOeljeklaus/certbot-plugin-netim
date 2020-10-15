import zope.interface
import logging

from time import sleep

from certbot import interfaces, errors
from certbot.plugins import dns_common

from . import netim_acme_dns_challenge_webui_client

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for netim (using unofficial webui client)."""

    description = 'Obtain certificates using a DNS TXT record (if you are using netim for DNS).'

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self.session = netim_acme_dns_challenge_webui_client.init_session()

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='netim credentials INI file.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'an unofficial netim webui client.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'netim credentials INI file',
            {
                'username': 'Login username for netim account, also referred to as handle',
                'password': 'Login password for netim account',
            },        
        )
        assert netim_acme_dns_challenge_webui_client.login(sess=self.session, login=self.credentials.conf('username'), pwd=self.credentials.conf('password'))

    def _perform(self, domain, validation_name, validation):
        assert validation_name[:15]=='_acme-challenge'
        assert netim_acme_dns_challenge_webui_client.create_dns_challenge(sess=self.session, domain=domain, challengeval=validation)
        sleep(5*60) # wait 5 mins, propagation can be slow

    def _cleanup(self, domain, validation_name, validation):
        assert netim_acme_dns_challenge_webui_client.remove_dns_challenge(sess=self.session,domain=domain)
        assert netim_acme_dns_challenge_webui_client.logout(sess=self.session)
