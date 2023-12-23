import logging

from django.conf import settings as django_settings
from extras.plugins import PluginConfig
from netbox.settings import VERSION
from pydantic import BaseModel, Field

from validity.utils.version import NetboxVersion


logger = logging.getLogger(__name__)


class NetBoxValidityConfig(PluginConfig):
    name = "validity"
    verbose_name = "Validity: Configuration Compliance"
    description = "Vendor-agnostic framework to build your own configuration compliance rule set"
    author = "Anton Miasnikov"
    author_email = "anton2008m@gmail.com"
    version = "1.4.2"
    base_url = "validity"
    django_apps = ["bootstrap5"]
    min_version = "3.4.0"

    # custom field
    netbox_version = NetboxVersion(VERSION)

    def ready(self):
        import validity.data_backends

        return super().ready()


config = NetBoxValidityConfig


class ValiditySettings(BaseModel):
    store_last_results: int = Field(default=5, gt=0, lt=1001)
    store_reports: int = Field(default=5, gt=0, lt=1001)
    sleep_between_tests: float = 0
    result_batch_size: int = 500


settings = ValiditySettings.model_validate(django_settings.PLUGINS_CONFIG.get("validity", {}))
