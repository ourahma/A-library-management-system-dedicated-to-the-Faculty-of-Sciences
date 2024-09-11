# Generated by Django 5.0.4 on 2024-05-02 23:10

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Personne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('image', models.ImageField(blank=True, default='assets/profile_user.jpeg', null=True, upload_to='uploads/users/image/')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('telephone', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('role', models.CharField(choices=[('UTILISATEUR', 'Utilisateur'), ('ADHERENT', 'Adherent'), ('ADMINSUP', 'AdminSup')], default='UTILISATEUR', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id_categorie', models.AutoField(primary_key=True, serialize=False)),
                ('nom_categorie', models.CharField(max_length=100)),
                ('description_categorie', models.CharField(default='', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Visiteur',
            fields=[
                ('idv', models.AutoField(primary_key=True, serialize=False)),
                ('adresse_ip', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Adherent',
            fields=[
                ('personne_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to=settings.AUTH_USER_MODEL)),
                ('id_adherant', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('biblio_app.personne',),
        ),
      
        migrations.CreateModel(
            name='Ouvrage',
            fields=[
                ('ISBN', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('titre', models.CharField(max_length=80)),
                ('type', models.CharField(max_length=20)),
                ('auteur', models.CharField(max_length=50)),
                ('edition', models.CharField(max_length=80)),
                ('image', models.ImageField(upload_to='uploads/ouvrage/')),
                ('description', models.CharField(default='', max_length=300)),
                ('num_exemplaire', models.PositiveIntegerField(default=0)),
                ('num_exmp_dispo', models.PositiveIntegerField(default=0)),
                ('categorie', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='biblio_app.categorie')),
            ],
        ),
        migrations.CreateModel(
            name='Exemplaire',
            fields=[
                ('id_exemplaire', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('deteriore', models.BooleanField(default=False)),
                ('emprunte', models.BooleanField(default=False)),
                ('perdu', models.BooleanField(default=False)),
                ('disponible', models.BooleanField(default=True)),
                ('ouvrage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.ouvrage')),
            ],
        ),
        migrations.CreateModel(
            name='Gerer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISBN', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.ouvrage')),
                ('ida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.personne')),
            ],
        ),
    
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id_reservation', models.AutoField(primary_key=True, serialize=False)),
                ('date_reservation', models.DateField(auto_now_add=True)),
                ('ouvrage', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='biblio_app.ouvrage')),
                ('id_utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.personne')),
            ],
        ),
        migrations.CreateModel(
            name='Emprunter',
            fields=[
                ('id_emprunt', models.AutoField(primary_key=True, serialize=False)),
                ('date_sortie', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_retour', models.DateTimeField(blank=True, null=True)),
                ('exemplaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.exemplaire')),
                ('ouvrage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.ouvrage')),
                ('adherant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.personne')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.personne')),
            ],
        ),
        migrations.CreateModel(
            name='Rechercher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.ouvrage')),
                ('idv', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='biblio_app.visiteur')),
            ],
            options={
                'unique_together': {('idv', 'isbn')},
            },
        ),
    ]
