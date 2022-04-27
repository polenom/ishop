# Generated by Django 4.0.4 on 2022-04-27 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0004_alter_client_clientcountry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorName', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Buy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyDescription', models.CharField(default='', max_length=50)),
                ('buyClient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buy', to='ishop.client', verbose_name='client')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryName', models.CharField(max_length=30, unique=True)),
                ('categorySlug', models.SlugField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genreName', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Motoroils',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motoroilsTitle', models.CharField(default='', max_length=200)),
                ('motoroilsSlug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Oilproducer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oilproducer', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stepName', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='city',
            name='cityName',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='ishop.category', verbose_name='product')),
            ],
        ),
        migrations.CreateModel(
            name='Motoroilsvolums',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motoroilsvolumsPrice', models.FloatField()),
                ('motoroilsvolumsCount', models.IntegerField()),
                ('motoroilsvolumsVolums', models.FloatField()),
                ('motoroilsvolums', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oilvolume', to='ishop.motoroils')),
            ],
        ),
        migrations.AddField(
            model_name='motoroils',
            name='motoroilsProducer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='oil', to='ishop.oilproducer'),
        ),
        migrations.CreateModel(
            name='Buy_step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buystepDatestart', models.DateTimeField(null=True)),
                ('buystepDatefinish', models.DateTimeField(null=True)),
                ('buystepBuy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ishop.buy', verbose_name='buystep')),
                ('buystepStep', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ishop.step')),
            ],
        ),
        migrations.CreateModel(
            name='Buy_product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyproductCount', models.IntegerField(default=1)),
                ('buyproductBuy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyproduct', to='ishop.buy', verbose_name='buyproduct')),
                ('buyproductProduct', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='buyproduct', to='ishop.product', verbose_name='buyproduct')),
            ],
        ),
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booksTitle', models.CharField(max_length=100)),
                ('booksDiscription', models.CharField(default='', max_length=300)),
                ('booksPrice', models.FloatField()),
                ('booksCount', models.IntegerField()),
                ('booksSlug', models.SlugField(unique=True)),
                ('booksAuthor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='ishop.author', verbose_name='author')),
                ('booksGenre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ishop.genre', verbose_name='books')),
                ('booksProduct', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='book', to='ishop.product')),
            ],
        ),
    ]
