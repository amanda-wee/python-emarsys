"""
Copyright 2012 42 Ventures Pte Ltd

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import base64
import datetime
import hashlib
import random
import requests
try:
    import simplejson as json
    assert json  # Silence potential warnings from static analysis tools
except ImportError:
    import json


class Emarsys(object):
    """
    Emarsys REST API wrapper.
    """

    class Error(Exception):
        """
        Exception raised when an Emarsys REST API call fails either due to a
        network related error or for an Emarsys specific reason.
        """
        def __init__(self, message, code=None):
            self.message = message
            self.code = code
            if self.code is not None:
                try:
                    self.code = int(self.code)
                except ValueError:
                    pass

        def __unicode__(self):
            if self.code is None:
                message = self.message
            else:
                message = u"{message} ({code})".format(message=self.message,
                                                       code=self.code)
            return u"Emarsys.Error({message})".format(message=message)

        def __str__(self):
            return unicode(self).encode("utf8")

        def __repr__(self):
            return str(self)

    def __init__(self,
                 username,
                 secret_token,
                 base_uri=u"https://www1.emarsys.net/api/v2/",
                 tzinfo_obj=None):
        """
        Initialises the Emarsys API wrapper object.
        """
        self._username = username
        self._secret_token = secret_token
        self._base_uri = base_uri
        self._tzinfo_obj = tzinfo_obj

    def __unicode__(self):
        return u"Emarsys({base_uri})".format(base_uri=self._base_uri)

    def __repr__(self):
        return unicode(self).encode("utf8")

    def call(self, uri, method, params=None):
        """
        Send the API call request to the Emarsys server.
        uri: API method URI
        method: HTTP method
        params: parameters to construct payload when API calls are made with
                POST or PUT HTTP methods.
        """
        uri = self._base_uri + uri
        if params:
            params = json.dumps(params)
        headers = {"X-WSSE": self._authentication_header_value(),
                   "Content-Type": "application/json"}
        try:
            response = requests.request(method,
                                        uri,
                                        data=params,
                                        headers=headers)
        except Exception as e:
            raise self.Error(message=repr(e))

        if response.status_code in (401, 404):
            raise self.Error(
                message=u"HTTP {status_code}: {reason} [{uri}]".format(
                    status_code=response.status_code,
                    reason=response.reason,
                    uri=uri,
                ),
            )

        try:
            result = json.loads(response.text)
        except ValueError as e:
            raise self.Error(message=repr(e))

        if not (isinstance(result, dict) and "replyCode" in result and
                "replyText" in result and "data" in result):
            message = u"Unexpected response from Emarsys"
            if not response.ok:
                message = u"{message} (HTTP {status_code})".format(
                    message=message,
                    code=response.status_code,
                )
            raise self.Error(message=message)

        if result["replyCode"] != 0:
            raise self.Error(message=result["replyText"],
                             code=result["replyCode"])

        return result["data"]

    def _authentication_header_value(self):
        now = datetime.datetime.now(self._tzinfo_obj)
        created = now.replace(microsecond=0).isoformat()
        nonce = hashlib.md5(str(random.getrandbits(128))).hexdigest()
        password_digest = "".join((nonce, created, self._secret_token))
        password_digest = hashlib.sha1(password_digest).hexdigest()
        password_digest = base64.b64encode(password_digest)
        return ('UsernameToken Username="{username}", '
                'PasswordDigest="{password_digest}", Nonce="{nonce}", '
                'Created="{created}"').format(username=self._username,
                                              password_digest=password_digest,
                                              nonce=nonce,
                                              created=created)
