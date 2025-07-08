from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0002_add_sample_dealers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealercenter',
            name='dealer_type',
            field=models.CharField(
                choices=[
                    ('factory', 'Главный завод'),
                    ('official', 'Официальный дилер'),
                    ('authorized', 'Авторизованный дилер'),
                    ('partner', 'Партнер'),
                    ('distributor', 'Дистрибьютор')
                ],
                default='official',
                max_length=20,
                verbose_name='Тип дилера'
            ),
        ),
        migrations.AlterField(
            model_name='dealercenter',
            name='sort_order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Чем меньше число, тем выше в списке. Заводы всегда показываются первыми.',
                verbose_name='Порядок сортировки'
            ),
        ),
    ]