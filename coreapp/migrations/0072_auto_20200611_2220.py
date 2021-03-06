# Generated by Django 2.2 on 2020-06-11 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0071_project_delete_obj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plot',
            name='plot_type',
            field=models.CharField(choices=[('scatter_2d', 'scatter_2d'), ('scatter_3d', 'scatter_3d'), ('bar', 'bar'), ('line_2d', 'line_2d'), ('line_3d', 'line_3d'), ('histogram', 'histogram'), ('box_plot', 'box_plot'), ('time_series_plot', 'time_series_plot'), ('bubble_plot', 'bubble_plot'), ('heatmap', 'heatmap'), ('pie_chart', 'pie_chat'), ('horizontal_bar', 'horizontal_bar'), ('cat', 'cat'), ('count', 'count')], max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_duration',
            field=models.CharField(blank=True, choices=[('1 Month', '1 Month'), ('3 Months', '3 Months'), ('6 Months', '6 Months'), ('12 Months', '12 Months')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='projectdashboard',
            name='dashboard_for',
            field=models.CharField(choices=[('Public', 'Public'), ('Me Only', 'Me Only'), ('Project Users', 'Project Users')], max_length=30),
        ),
    ]
