from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('ckk', '0042_auto_20190426_1017'),
    ]
    atomic = True

    operations = [
        # migrations.RunSQL(
        #     f"""insert into ckk_status(lastmodified , editing, deliting, code, name, description )
        #                             values('NOW()', 'false' , 'false' ,'new', 'Новый', null )"""
        # ),

    ]
