# Generated for nearest bin map feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='garbagebin',
            name='waste_type',
            field=models.CharField(choices=[('e_waste', 'E-Waste'), ('eco_friendly', 'Eco-Friendly Waste'), ('mixed', 'Mixed Waste')], default='mixed', help_text='Type of waste accepted by this bin', max_length=20),
        ),
    ]
