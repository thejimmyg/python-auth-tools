import os
from dataclasses import dataclass

from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import Config
from saml2.sigver import get_xmlsec_binary

from config import config_url
from helper_log import helper_log

config_saml_sp_slack_seconds = float(os.environ.get("SAML_SP_SLACK_SECONDS", 0))
helper_log(
    __file__,
    "Allowing slack in the SAML time of",
    config_saml_sp_slack_seconds,
    "seconds",
)


@dataclass
class IdPConfig:
    entity_id: str
    single_sign_on_url: str
    x509_cert: str

    def __hash__(self):
        return hash(self.entity_id)


if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"])
else:
    xmlsec_path = "/usr/bin/xmlsec1"


def saml_client():
    saml_settings = {
        # Currently xmlsec1 binaries are used for all the signing and encryption stuff.This option defines where the binary is situated.
        "xmlsec_binary": xmlsec_path,
        # The SP ID. It is recommended that the entityid should point to a real webpage where the metadata for the entity can be found.
        "entityid": config_url + "/sample_sp",
        # Indicates that attributes that are not recognized (they are not configured in attribute-mapping), will not be discarded.
        "allow_unknown_attributes": True,
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        ##as mentioned in the sequence diagram we can use either redirect or post here.
                        (config_url + "/saml2/acs/", BINDING_HTTP_POST),
                    ]
                },
                # Don't verify that the incoming requests originate from us via the built-in cache for authn request ids in pysaml2
                "allow_unsolicited": True,
                # Don't sign authn requests, since signed requests only make sense in a situation where you control both the SP and IdP
                "authn_requests_signed": False,
                # Assertion must be signed
                "want_assertions_signed": True,
                # Response signing is optional.
                "want_response_signed": False,
            }
        },
        "metadata": [
            {
                "class": "store_saml_sp.MetaDataIdP",
                "metadata": [
                    (
                        IdPConfig(
                            entity_id="oktadev/test/sample-sp",
                            single_sign_on_url="http://idp.oktadev.com",
                            x509_cert="MIIDPDCCAiQCCQDydJgOlszqbzANBgkqhkiG9w0BAQUFADBgMQswCQYDVQQGEwJVUzETMBEGA1UECBMKQ2FsaWZvcm5pYTEWMBQGA1UEBxMNU2FuIEZyYW5jaXNjbzEQMA4GA1UEChMHSmFua3lDbzESMBAGA1UEAxMJbG9jYWxob3N0MB4XDTE0MDMxMjE5NDYzM1oXDTI3MTExOTE5NDYzM1owYDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWExFjAUBgNVBAcTDVNhbiBGcmFuY2lzY28xEDAOBgNVBAoTB0phbmt5Q28xEjAQBgNVBAMTCWxvY2FsaG9zdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMGvJpRTTasRUSPqcbqCG+ZnTAurnu0vVpIG9lzExnh11o/BGmzu7lB+yLHcEdwrKBBmpepDBPCYxpVajvuEhZdKFx/Fdy6j5mH3rrW0Bh/zd36CoUNjbbhHyTjeM7FN2yF3u9lcyubuvOzr3B3gX66IwJlU46+wzcQVhSOlMk2tXR+fIKQExFrOuK9tbX3JIBUqItpI+HnAow509CnM134svw8PTFLkR6/CcMqnDfDK1m993PyoC1Y+N4X9XkhSmEQoAlAHPI5LHrvuujM13nvtoVYvKYoj7ScgumkpWNEvX652LfXOnKYlkB8ZybuxmFfIkzedQrbJsyOhfL03cMECAwEAATANBgkqhkiG9w0BAQUFAAOCAQEAeHwzqwnzGEkxjzSD47imXaTqtYyETZow7XwBc0ZaFS50qRFJUgKTAmKS1xQBP/qHpStsROT35DUxJAE6NY1Kbq3ZbCuhGoSlY0L7VzVT5tpu4EY8+Dq/u2EjRmmhoL7UkskvIZ2n1DdERtd+YUMTeqYl9co43csZwDno/IKomeN5qaPc39IZjikJ+nUC6kPFKeu/3j9rgHNlRtocI6S1FdtFz9OZMQlpr0JbUt2T3xS/YoQJn6coDmJL5GTiiKM6cOe+Ur1VwzS1JEDbSS2TWWhzq8ojLdrotYLGd9JOsoQhElmz+tMfCFQUFLExinPAyy7YHlSiVX13QH2XTu/iQQ==",
                        ),
                    )
                ],
            }
        ],
        "accepted_time_diff": config_saml_sp_slack_seconds,
    }

    helper_log(
        __file__,
        "Allowing slack in the SAML time of",
        saml_settings["accepted_time_diff"],
        "seconds",
    )
    config = Config()
    config.load(saml_settings)

    return Saml2Client(config=config)
