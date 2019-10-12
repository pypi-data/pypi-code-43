from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('input', '0001_initial'),
    ]
    atomic = True

    operations = [
        migrations.RunSQL(
            f"""insert into input_operation_plan_types(lastmodified , editing, deliting, code, name)
                                    values('NOW()', 'false' , 'false' ,'Manufacturing-Order', 'Заказы на продажу')"""
        ),
        migrations.RunSQL(
            f"""insert into input_operation_plan_types(lastmodified , editing, deliting, code, name)
                                        values('NOW()', 'false' , 'false' ,'Distribution-Order', 'Заказы на распределение')"""
        ),
        migrations.RunSQL(
            f"""insert into input_operation_plan_types(lastmodified , editing, deliting, code, name)
                                        values('NOW()', 'false' , 'false' ,'Purchase-Order', 'Заказы на закупку')"""
        ),
        migrations.RunSQL(
            f"""insert into input_operation_plan_types(lastmodified , editing, deliting, code, name)
                                        values('NOW()', 'false' , 'false' ,'Delivery-Order', 'Заказы на доставку')"""
        )
    ]
