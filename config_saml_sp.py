import os

from helper_log import helper_log

config_saml_sp_slack_seconds = float(os.environ.get("SAML_SP_SLACK_SECONDS", 0))
helper_log(
    __file__,
    "Allowing slack in the SAML time of",
    config_saml_sp_slack_seconds,
    "seconds",
)
