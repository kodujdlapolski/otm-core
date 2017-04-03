# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0042_auto_20170112_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreeProblem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('tree', models.ForeignKey(to='treemap.Tree')),
            ],
        ),
        migrations.CreateModel(
            name='TreeProblemCatalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='treeproblem',
            name='tree_problem',
            field=models.ForeignKey(to='treemap.TreeProblemCatalog'),
        ),
        migrations.AddField(
            model_name='treeproblem',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
