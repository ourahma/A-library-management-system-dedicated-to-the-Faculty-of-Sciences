from typing import Any
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.db.models import F
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
import base64
from django.contrib.admin.models import LogEntry
from django.contrib.admin import site

class Categorie(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    nom_categorie = models.CharField(max_length=100)
    description_categorie = models.CharField(max_length=300, default='')

    def __str__(self):         
        return self.nom_categorie
    
    def Ajouter_Categorie(nom_categorie, description_categorie):
        cat = Categorie(nom_categorie=nom_categorie,description_categorie=description_categorie)
        cat.save()

    def modifier_categorie(self, categorie_id, nouveau_nom,nouvelle_description):
        categorie = Categorie.objects.get(id_categorie=categorie_id)

        categorie.nom_categorie = nouveau_nom
        categorie.description_categorie = nouvelle_description
        
        categorie.save()
      
    
    def supprimer_categorie(self, categorie_id):
        try:
            categorie = Categorie.objects.get(id_categorie=categorie_id)
            categorie.delete()
            return True 
        except ObjectDoesNotExist:
            return False 

 
class Ouvrage(models.Model):
    ISBN  = models.CharField(max_length=100,primary_key=True)
    titre = models.CharField(max_length=80)
    type = models.CharField(max_length=20)
    auteur  = models.CharField(max_length=50)
    categorie  = models.ForeignKey(Categorie , on_delete=models.CASCADE , default=1)
    edition  = models.CharField(max_length=80)
    
    image = models.ImageField(upload_to='uploads/ouvrage/')
    description =models.CharField(max_length=300,default='')

    num_exemplaire = models.PositiveIntegerField(default=0)
    num_exmp_dispo = models.PositiveIntegerField(default=0)
    


    def __str__(self):
        return f'{self.ISBN} {self.titre} '
    
    def ajouter_ouvrage(self, titre, auteur, edition, ISBN , type, categorie,image,description):
        new_ouvrage = Ouvrage(titre=titre, auteur=auteur, edition=edition, ISBN = ISBN,type=type, categorie=categorie,image=image,description=description)
        new_ouvrage.save()

    def modifier_ouvrage(self, isbn_g, nouveau_titre, nouveau_auteur, nouvelle_edition, nouveau_type, nouvelle_categorie,nouvelle_image,nouvelle_description):
            ouvrage = Ouvrage.objects.get(ISBN=isbn_g)

            ouvrage.titre = nouveau_titre
            ouvrage.auteur = nouveau_auteur
            ouvrage.edition = nouvelle_edition
            ouvrage.type = nouveau_type
            ouvrage.categorie = nouvelle_categorie
            ouvrage.image=nouvelle_image
            ouvrage.description = nouvelle_description

            ouvrage.save()
           

    def supprimer_ouvrage(self, ISBN):
        try:
            ouvrage = Ouvrage.objects.get(ISBN=ISBN)
            ouvrage.delete()
            return True
        except Ouvrage.DoesNotExist:
            return False
        
        
class PersonneManager(BaseUserManager):
    def create_superuser(self, email, password, nom, prenom,telephone=None,role="ADMINSUP",image_data =None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if telephone is None:
            telephone = ""
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        new = Personne(email=email,nom=nom,telephone=telephone,prenom=prenom,role='ADMINSUP',
                    is_staff = True,
                    is_superuser=True,)
        new.set_password(password)
        admin = new.save()
        print(new)
        
        return admin
    
    def create_user(self, email, password, nom, prenom, telephone,role='UTILISATEUR',image_data=None,**extra_fields):
        if not email:
            raise ValueError('L\'adresse e-mail est obligatoire')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        
        if image_data:
            format, imgstr = image_data.split(';base64,')  # Split the base64 data
            ext = format.split('/')[-1]  # Extract the extension
            # Create the file name
            image_name = f"{user.email}_profile_pic.{ext}"
            # Decode and save the image
            data = ContentFile(base64.b64decode(imgstr), name=image_name)
            user.image.save(image_name, data, save=True)
        user.save()
        return user


class Personne(AbstractBaseUser, PermissionsMixin):
    image = models.ImageField(upload_to='uploads/users/image/', null=True, blank=True,default="assets/profile_user.jpeg")
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    password=models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    banni = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom','prenom','password']
    
    ROLE_CHOICES = (
        ('UTILISATEUR', 'Utilisateur'),
        ('BIBLIOTHECAIRE', 'Bibliothecaire'),
        ('ADMINSUP', 'AdminSup'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='UTILISATEUR')
    
    objects = PersonneManager()

    def __str__(self):
        return self.email
    
    def Ajouter_bibliothecaire(nom, prenom, telephone, email, password):
        # Hash the password
        hashed_password = make_password(password)

        # Create an Bibliothecaire instance
        bibliothecaire = Personne.objects.create(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            password=hashed_password,  # Save the hashed password
            role = 'BIBLIOTHECAIRE',
            is_staff = True
        )

        return bibliothecaire

    def Modifier_bibliothecaire(self, adh_id, n_nom ,n_prenom , n_telephone,n_email , n_password='' ):
        bibliothecaire= Personne.objects.get(id = adh_id, role = 'BIBLIOTHECAIRE')
        if n_password != '' :
            hashed_password = make_password(n_password)
            bibliothecaire.password = hashed_password
        bibliothecaire.nom = n_nom
        bibliothecaire.prenom = n_prenom
        bibliothecaire.email = n_email
        bibliothecaire.telephone = n_telephone
        bibliothecaire.role = 'BIBLIOTHECAIRE'

        bibliothecaire.save()
        print("done")


    def supprimer_bibliothecaire(self, id):
            try:
                bibliothecaire = Personne.objects.get(id = id, role = 'BIBLIOTHECAIRE')
                bibliothecaire.delete()
                return True 
            except ObjectDoesNotExist as e:
                print(e)
                return False
            

    def signaler_perte(self, exemplaire):
        if isinstance(exemplaire, Exemplaire) and exemplaire:
            exemplaire.perdu = True
            exemplaire.empruntable=False
            exemplaire.disponible=False
            exemplaire.save()

            ouvrage = exemplaire.ouvrage
            ouvrage.num_exmp_dispo = max(ouvrage.num_exmp_dispo - 1, 0)  # Ensuring it doesn't go negative
            ouvrage.save()

            # Log the signalment in the Signalement table
            Signalement.objects.create(
                utilisateur=self,
                ouvrage=ouvrage,
                exemplaire=exemplaire
            )
            return True
        else:
            return False

    def signaler_deterioration(self, exemplaire):
        if isinstance(exemplaire, Exemplaire) and exemplaire:
            exemplaire.deteriore = True
            exemplaire.empruntable=False
            exemplaire.disponible=False
            exemplaire.save()

            ouvrage = exemplaire.ouvrage
            ouvrage.num_exmp_dispo = max(ouvrage.num_exmp_dispo - 1, 0)  
            ouvrage.save()

            Signalement.objects.create(
                utilisateur=self,
                ouvrage=ouvrage,
                exemplaire=exemplaire
            )
            return True
        else:
            return False
        
    def supprimer_signalement(self, signalement_id):
        try:
            signalement = Signalement.objects.get(id=signalement_id)

           
            exemplaire = signalement.exemplaire
            exemplaire.perdu = False
            exemplaire.deteriore = False
            exemplaire.empruntable=True
            exemplaire.disponible=True
            exemplaire.save()

           
            ouvrage = signalement.ouvrage
            ouvrage.num_exmp_dispo = F('num_exmp_dispo') + 1
            ouvrage.save()

            # Delete signalement entry
            signalement.delete()

            return 1, "Signalement supprimé avec succès"
        except Signalement.DoesNotExist:
            return 0, "Le signalement n'existe pas ou vous n'avez pas l'autorisation de le supprimer"
        
    def est_banni(self) :
        return self.banni
    
    def bannir(self) :
        self.banni = True
        self.save()

    def debannir(self) :
        self.banni = False
        self.save()


class Exemplaire(models.Model):
    id_exemplaire = models.AutoField(primary_key=True,unique=True)
    deteriore = models.BooleanField(default=False)
    perdu = models.BooleanField(default=False)
    empruntable = models.BooleanField(default=True)
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ouvrage.titre} - Exemplaire {self.id_exemplaire}"

    def __init__(self, *args, **kwargs):
        super(Exemplaire, self).__init__(*args, **kwargs)
        
        # Initialisation des attributs avec des valeurs par défaut
        if self.pk is None:    
            self.deteriore = False 
            self.perdu = False  

    def save(self, *args, **kwargs):
        # Check if the exemplaire is being created or updated
        created = not self.pk

        super().save(*args, **kwargs)  # Call the original save method

        # Update the num_exemplaire and num_exmp_dispo fields of the associated ouvrage
        self.update_ouvrage_counts(created=created, deleted = False)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)  # Call the original delete method
        # Update the num_exemplaire and num_exmp_dispo fields of the associated ouvrage
        self.update_ouvrage_counts(created=False, deleted = True)

    def update_ouvrage_counts(self, created=False, deleted=False):
        ouvrage = self.ouvrage
        # Increment num_exemplaire if the exemplaire is being created
        if created:
            ouvrage.num_exemplaire += 1
        if deleted :
            ouvrage.num_exemplaire -= 1
        # Update num_exmp_dispo based on the disponibility of the exemplaire
       
        ouvrage.num_exmp_dispo = Exemplaire.objects.filter(ouvrage=ouvrage, disponible=True).count()
        ouvrage.save()

    def add_exemplaire(deteriore ,perdu , ouvrage, empruntable , disponible):
        ex = Exemplaire(deteriore=deteriore, perdu=perdu, empruntable=empruntable, ouvrage=ouvrage, disponible=disponible)
        ex.save()
        
        #ex.update_ouvrage_counts(created=True)
        #ouvrage.save()

    def Modifier_exemplaire(self, id_ex, ndeteriore , nperdu, nempruntable , nouvrage ,  ndisponible ):
        exemplaire= Exemplaire.objects.get(id_exemplaire = id_ex)

        exemplaire.deteriore = ndeteriore
        exemplaire.perdu = nperdu
        exemplaire.empruntable = nempruntable
        exemplaire.ouvrage = nouvrage
        exemplaire.disponible = ndisponible
        exemplaire.update_ouvrage_counts()
        exemplaire.save()
        print("done")


    def delete_exemplaire(self, id_exemplaire):
            try:
                exemplaire = Exemplaire.objects.get(id_exemplaire = id_exemplaire)
                exemplaire.update_ouvrage_counts(deleted=True)
                exemplaire.delete()
                return True 
            except ObjectDoesNotExist:
                return False
    
    @classmethod   
    def get_all_exemplaires(cls):
        try:
            exemplaires = Exemplaire.objects.all()
        except Exemplaire.DoesNotExist:
            exemplaires = []
        return exemplaires
    
    
    
class Emprunter(models.Model):
    id_emprunt = models.AutoField(primary_key=True) 
    exemplaire = models.ForeignKey(Exemplaire, on_delete=models.CASCADE) 
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    bibliothecaire_id = models.ForeignKey(Personne, on_delete=models.CASCADE,related_name="emprunter_bibliothecaire",null=True)
    utilisateur = models.ForeignKey(Personne, on_delete=models.CASCADE,related_name="emprunter_utilisateur",null=True)
    date_sortie = models.DateTimeField(blank=True, null=True)
    date_retour = models.DateTimeField(blank=True, null=True)
    date_rendu = models.DateTimeField(blank=True, null=True)
    rendu = models.BooleanField(default=False)
    num_extensions=models.IntegerField(default=0)

    def __str__(self):
        return f'{self.utilisateur} {self.ouvrage} {self.exemplaire}'
    
    def Annuler_Emprunt(id_emprunt):
        try:
            emprunt = Emprunter.objects.get(id_emprunt=id_emprunt)
            exemplaire = Exemplaire.objects.get(id_exemplaire = emprunt.exemplaire.id_exemplaire)
            
            # L'emprunt n'est pas encore retourné, on peut l'annuler
            emprunt.delete()
            exemplaire.disponible = True
            exemplaire.save()
            exemplaire.update_ouvrage_counts()
            return True
        except ObjectDoesNotExist :
            # L'emprunt est déjà retourné, on ne peut pas l'annuler
            return False
        

    def Retourner_Emprunt(id_emprunt):
        try:
            emprunt = Emprunter.objects.get(id_emprunt=id_emprunt)
            exemplaire = Exemplaire.objects.get(id_exemplaire = emprunt.exemplaire.id_exemplaire)
            # L'emprunt n'est pas encore retourné, on peut l'annuler
            
            emprunt.rendu  = True
            emprunt.date_rendu = timezone.now()
            emprunt.save()
            exemplaire.disponible = True
            exemplaire.save()
            exemplaire.update_ouvrage_counts()
            return True
        except ObjectDoesNotExist :
            # L'emprunt est déjà retourné, on ne peut pas l'annuler
            return False


    def emprunter(id_ouvrage, id_bibliothecaire, id_utilisateur):
        ouvrage = Ouvrage.objects.get(ISBN=id_ouvrage)
        utilisateur = Personne.objects.get(email=id_utilisateur, role = 'UTILISATEUR')
        if not utilisateur.est_banni() :
            existing_emprunt = Emprunter.objects.filter(utilisateur=utilisateur, rendu=False)
            if len(existing_emprunt) <= 3 :
                if ouvrage.num_exmp_dispo > 1:
                    
                    exemplaire = Exemplaire.objects.filter(ouvrage=id_ouvrage, disponible=True, empruntable=True).first()
                    print(exemplaire)
                    if exemplaire and exemplaire.empruntable:
                        exemplaire.disponible = False
                        exemplaire.save()
                        exemplaire.update_ouvrage_counts()
                        
                        # Retrieve other necessary objects
                        ouvrage = Ouvrage.objects.get(ISBN=id_ouvrage)
                        bibliothecaire = Personne.objects.get(email=id_bibliothecaire, role = 'BIBLIOTHECAIRE')
                        
                        
                        # Calculate the return date (7 days from now)
                        date_retour = timezone.now() + timezone.timedelta(days=7)
                        
                        # Create and save the Emprunter instance
                        Emprunter.objects.create(exemplaire=exemplaire, ouvrage=ouvrage, bibliothecaire_id=bibliothecaire, utilisateur=utilisateur, date_retour=date_retour, rendu=False)
                        
                        return True,0, "Emprunt effectué avec succès."
                    else:
                        return False,0, "Aucun exemplaire disponible pour cet ouvrage, ou l'exemplaire n'est pas empruntable"
                else:
                    return False,1, "Vous ne pouvez faire qu'une consultation sur place."
            else:
                return False,0, "Cet utilisateur a atteint le nombre maximum d'emprunts!"
        else:
                return False,0, "Cet utilisateur est banni!"
        

    def modifier_emprunt(self,id_exemplaire, id_ouvrage, id_bibliothecaire, new_date, rendu=False, date_rendu=None):
        
        try :
            old_exemplaire = Exemplaire.objects.get(id_exemplaire=self.exemplaire.id_exemplaire)
            old_exemplaire.disponible= True
            old_exemplaire.save()
            old_exemplaire.update_ouvrage_counts()
            exemplaire = Exemplaire.objects.get(id_exemplaire=id_exemplaire)
            
            if exemplaire.disponible and exemplaire.empruntable :
                exemplaire.disponible= False
                exemplaire.save()
                exemplaire.update_ouvrage_counts()
                self.exemplaire = exemplaire
                print(exemplaire.id_exemplaire)
                self.id_ouvrage = Ouvrage.objects.get(ISBN=id_ouvrage)
                self.id_bibliothecaire = Personne.objects.get(email=id_bibliothecaire, role = 'BIBLIOTHECAIRE')
                new_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                self.date_sortie = new_date
                print(self.date_sortie)
                self.date_retour = new_date + timezone.timedelta(days=7)
                self.rendu=rendu
                self.date_rendu = date_rendu

                self.save()
                return True
            elif not exemplaire.empruntable:
                return False
            else :
                return False
            
        except ObjectDoesNotExist :
            return False
        

class Consulter(models.Model):
    id_consultation = models.AutoField(primary_key=True)
    exemplaire = models.ForeignKey(Exemplaire, on_delete=models.CASCADE)
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    bibliothecaire = models.ForeignKey(Personne, on_delete=models.CASCADE,related_name="consulter_bibliothecaire")
    utilisateur = models.ForeignKey(Personne, on_delete=models.CASCADE,related_name="consulter_utilisateur")
    date_sortie = models.DateTimeField(default=timezone.now)
    date_retour = models.DateTimeField(null=True, blank=True)
    rendu = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.utilisateur} {self.ouvrage} {self.exemplaire}'

    @staticmethod
    def consulter(id_ouvrage, id_bibliothecaire, id_utilisateur):
        ouvrage = Ouvrage.objects.get(ISBN=id_ouvrage)
        exemplaire = Exemplaire.objects.filter(ouvrage=id_ouvrage, disponible=True).first()
        utilisateur = Personne.objects.get(email=id_utilisateur, role = 'UTILISATEUR')
        if not utilisateur.est_banni() :
            if exemplaire:
                exemplaire.disponible = False
                exemplaire.save()
                exemplaire.update_ouvrage_counts()
                bibliothecaire = Personne.objects.get(email=id_bibliothecaire, role = 'BIBLIOTHECAIRE')
                Consulter.objects.create(exemplaire=exemplaire, ouvrage=ouvrage, bibliothecaire=bibliothecaire, utilisateur=utilisateur)
                return True, "Consultation effectuée avec succès."
            else:
                return False, "Aucun exemplaire n'est disponible."
        else:
                return False, "Cet utilisateur est banni!"
        
    
    def supprimer_consultation(id):
        try:
            consultation = Consulter.objects.get(id_consultation=id)
            exemplaire = Exemplaire.objects.get(id_exemplaire = consultation.exemplaire.id_exemplaire)
            # L'emprunt n'est pas encore retourné, on peut l'annuler
            consultation.delete()
            exemplaire.disponible = True
            exemplaire.save()
            exemplaire.update_ouvrage_counts()
            return True
        except ObjectDoesNotExist :
            # L'emprunt est déjà retourné, on ne peut pas l'annuler
            return False
        
    def retourner_consultation(id_consultation):
        try:
            consultation = Consulter.objects.get(id_consultation=id_consultation)
            exemplaire = Exemplaire.objects.get(id_exemplaire=consultation.exemplaire.id_exemplaire)
        
            consultation.rendu = True
            consultation.date_retour = timezone.now()
            consultation.save()
        
            exemplaire.disponible = True
            exemplaire.save()
            exemplaire.update_ouvrage_counts()
        
            return True
        except Consulter.DoesNotExist:
            return False
        except Exemplaire.DoesNotExist:
            return False
        
    def modifier_consultation(self, id_exemplaire, id_ouvrage, id_bibliothecaire, dateSortie, dateRetour):
        try:

            old_exemplaire = self.exemplaire
            old_exemplaire.disponible = True
            old_exemplaire.save()
            old_exemplaire.update_ouvrage_counts()

            exemplaire = Exemplaire.objects.get(id_exemplaire=id_exemplaire)
            if exemplaire and exemplaire.disponible:

                exemplaire.disponible = False
                exemplaire.save()
                exemplaire.update_ouvrage_counts()

                self.exemplaire = exemplaire
                self.ouvrage = Ouvrage.objects.get(titre=id_ouvrage)
                self.bibliothecaire = Personne.objects.get(email=id_bibliothecaire)
                self.date_sortie = datetime.strptime(dateSortie, '%Y-%m-%d').date()
                self.date_retour = datetime.strptime(dateRetour, '%Y-%m-%d').date()

                self.save()
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False


class Reservation(models.Model):
    id_reservation = models.AutoField(primary_key=True)
    date_reservation = models.DateField()
    date_emprunt=models.DateField()
    id_utilisateur = models.ForeignKey(Personne, on_delete=models.CASCADE)
    ouvrage=models.ForeignKey("Ouvrage", on_delete=models.CASCADE,default=None)
    def __str__(self):
        return f'{self.id_utilisateur} {self.date_reservation} {self.date_emprunt}'
    
    def reserver(id_a,id_u):
        r = Reservation(id_utilisateur=Personne.objects.get(id=id_u, role='UTILISATEUR'))
        r.save()
        
    

    def modify_reservation(self, reservation_id, new_date, id_u):
        try:
            reservation = Reservation.objects.get(id_reservation=reservation_id)
            
            reservation.date_reservation = new_date
            reservation.id_utilisateur = Personne.objects.get(id=id_u, role = 'UTILISATEUR')
            
            reservation.save()
            return True  
        except ObjectDoesNotExist:
            return False 
        
    def delete_reservation(self, reservation_id):
        try:
            reservation = Reservation.objects.get(id_reservation=reservation_id)
           
            reservation.ouvrage.num_exmp_dispo += 1
            reservation.ouvrage.save()  # Sauvegarder les modifications sur l'instance de l'ouvrage
            reservation.delete()
            return True
        except Reservation.DoesNotExist:
            return False
        except Exception as e:
          
            return False
        
        
class Gerer(models.Model):
    ida=models.ForeignKey(Personne, on_delete=models.CASCADE)
    ISBN=models.ForeignKey(Ouvrage,on_delete=models.CASCADE)
    

    

    def __str__(self):
        return f" GERER {self.ida} - {self.ISBN}"


class CustomLogEntry(LogEntry):
    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.action_time}: {self.user} - {self.get_action_flag_display()}"

    def get_model_name(self):
        # Récupérer le nom de la table à partir de ContentType
        return self.content_type.model

# Enregistrer le modèle personnalisé dans l'administration Django


class Notification(models.Model):
    user = models.ForeignKey(Personne, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.email} at {self.timestamp}'
    

class Signalement(models.Model) :
    utilisateur = models.ForeignKey(Personne,on_delete=models.CASCADE)
    ouvrage = models.ForeignKey(Ouvrage,on_delete=models.CASCADE)
    exemplaire = models.ForeignKey(Exemplaire,on_delete=models.CASCADE)


    def __str__(self) -> str:
        return f"signlement de {self.utilisateur} pour l exemplaire {self.exemplaire}"