from biblio_app.models import *
from django.core.cache import cache
from django.utils import timezone

class EmpruntDelai(models.Model) :
    def __init__(self,request):
        self.session=request.session
        
        #Get the current session key if it exists
        emprunt=self.session.get('session_key')
        
        #if the user is new no session, create one
        if 'session_key' not in request.session:
            emprunt = self.session['session_key']={}
        
        #make sure cart is available on all pages of site
        self.emprunt=emprunt


    @classmethod
    def get_overdue_emprunts(cls):
        # Check if the result is cached
        cache_key = 'overdue_emprunts'
        overdue_emprunts = cache.get(cache_key)

        if overdue_emprunts is None:
            # Calculate overdue emprunts
            overdue_emprunts = cls.objects.filter(date_retour__lt=timezone.now())
            
            # Cache the result for future use with an expiration time (e.g., 1 hour)
            cache.set(cache_key, overdue_emprunts, timeout=3600)

        return overdue_emprunts
    