# Generated by Django 4.2.7 on 2023-12-08 23:18

from django.db import migrations, models
import taggit.managers
import utilities.json
import validity.models.base
import validity.utils.dbfields
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


def create_cf(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    CustomField = apps.get_model("extras", "CustomField")
    Poller = apps.get_model("validity", "Poller")
    Device = apps.get_model("dcim", "Device")
    DeviceType = apps.get_model("dcim", "DeviceType")
    Manufacturer = apps.get_model("dcim", "Manufacturer")
    db_alias = schema_editor.connection.alias

    cf = CustomField.objects.using(db_alias).create(
        name="poller",
        label=_("Poller"),
        description=_("Required by Validity. Defines properties of device polling"),
        type="object",
        object_type=ContentType.objects.get_for_model(Poller),
        required=False,
    )
    cf.content_types.set(
        [
            ContentType.objects.get_for_model(Device),
            ContentType.objects.get_for_model(DeviceType),
            ContentType.objects.get_for_model(Manufacturer),
        ]
    )


def delete_cf(apps, schema_editor):
    CustomField = apps.get_model("extras", "CustomField")
    db_alias = schema_editor.connection.alias
    CustomField.objects.using(db_alias).filter(name="poller").delete()


def create_polling_datasource(apps, schema_editor):
    DataSource = apps.get_model("core", "DataSource")
    db = schema_editor.connection.alias
    ds = DataSource.objects.using(db).create(
        name="Validity Polling",
        type="device_polling",
        source_url="/",
        description=_("Required by Validity. Polls bound devices and stores the results"),
        custom_field_data={
            "device_config_path": "{{device | slugify}}/{{ device.poller.config_command.label }}.txt",
            "device_config_default": False,
            "web_url": "",
        },
    )
    ds.parameters = {"datasource_id": ds.pk}
    ds.save()


def delete_polling_datasource(apps, schema_editor):
    DataSource = apps.get_model("core", "DataSource")
    db = schema_editor.connection.alias
    DataSource.objects.using(db).filter(type="Validity Polling").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("validity", "0006_script_change"),
    ]

    operations = [
        migrations.CreateModel(
            name="Command",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "label",
                    models.CharField(
                        max_length=100,
                        unique=True,
                        validators=[
                            RegexValidator(
                                regex="^[a-z][a-z0-9_]*$",
                                message=_("Only lowercase ASCII letters, numbers and underscores are allowed"),
                            )
                        ],
                    ),
                ),
                ("retrieves_config", models.BooleanField(default=False)),
                ("type", models.CharField(max_length=50)),
                ("parameters", models.JSONField()),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(validity.models.base.URLMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Poller",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("connection_type", models.CharField(max_length=50)),
                ("public_credentials", models.JSONField(blank=True, default=dict)),
                ("private_credentials", validity.utils.dbfields.EncryptedDictField(blank=True)),
                ("commands", models.ManyToManyField(related_name="pollers", to="validity.command")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(validity.models.base.URLMixin, models.Model),
        ),
        migrations.RunPython(create_cf, delete_cf),
        migrations.RunPython(create_polling_datasource, delete_polling_datasource),
    ]
