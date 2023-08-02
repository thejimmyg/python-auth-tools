from saml2 import md, BINDING_HTTP_REDIRECT, samlp, xmldsig
from saml2.mdstore import InMemoryMetaData
from helper_saml_sp import IdPConfig


class MetaDataIdP(InMemoryMetaData):
    def __init__(self, attrc, metadata: IdPConfig):
        super(MetaDataIdP, self).__init__(attrc, metadata)
        self.metadata = metadata

    def load(self, *args, **kwargs):
        idpsso_descriptor = md.IDPSSODescriptor()
        idpsso_descriptor.protocol_support_enumeration = samlp.NAMESPACE
        idpsso_descriptor.single_sign_on_service = [
            md.SingleSignOnService(
                binding=BINDING_HTTP_REDIRECT, location=self.metadata.single_sign_on_url
            )
        ]
        idpsso_descriptor.key_descriptor = [
            md.KeyDescriptor(
                use="signing",
                key_info=xmldsig.KeyInfo(
                    x509_data=[
                        xmldsig.X509Data(
                            x509_certificate=xmldsig.X509Certificate(
                                text=self.metadata.x509_cert
                            )
                        )
                    ]
                ),
            )
        ]

        entity_descriptor = md.EntityDescriptor()
        entity_descriptor.entity_id = self.metadata.entity_id
        entity_descriptor.idpsso_descriptor = [idpsso_descriptor]
        self.do_entity_descriptor(entity_descriptor)
