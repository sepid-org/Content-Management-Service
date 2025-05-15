from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('meeting', '0004_remove_meeting_meeting_mee_start_t_6ebfbd_idx_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Cast the old time values into timestamps with TZ
            "ALTER TABLE apps_meeting "
            "ALTER COLUMN start_time "
            "TYPE timestamp with time zone "
            "USING start_time::timestamp with time zone;"
        ),
    ]
