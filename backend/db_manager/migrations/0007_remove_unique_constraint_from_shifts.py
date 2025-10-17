from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("db_manager", "0006_shiftrule_shiftexception_shifts_rule_shifttemplate_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="shifts",
            name="no_overlap_shifts_same_user",
        ),
    ]
