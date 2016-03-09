import os
import pycurl
import json
import sys
from urlparse import urljoin
from StringIO import StringIO

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        key = terms[0]
        try:
            field = terms[1]
        except:
            field = None

        url = os.getenv('VAULT_ADDR')
        if not url:
            raise AnsibleError('VAULT_ADDR environment variable is missing')

        token = os.getenv('VAULT_TOKEN')
        if not token:
            raise AnsibleError('VAULT_TOKEN environment variable is missing')

        request_url = urljoin(url, "v1/%s" % (key))

        buffer = StringIO()
        try:
            c = pycurl.Curl()
            c.setopt(c.URL, request_url)
            c.setopt(c.HTTPHEADER, ['X-Vault-Token: ' + token])
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            c.close()
        except:
            raise AnsibleError('Unable to read %s from vault' % key)

        result = json.loads(buffer.getvalue())

        return [result['data'][field]] if field is not None else result['data']
