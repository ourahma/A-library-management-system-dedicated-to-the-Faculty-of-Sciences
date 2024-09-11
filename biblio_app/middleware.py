from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.utils import timezone
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class UpdateOverdueEmpruntsCacheMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def update_overdue_emprunts_cache(self):
        # Calculate overdue emprunts
        overdue_emprunts = Emprunter.objects.filter(date_retour__lt=timezone.now())
        
        # Cache the result for future use with an expiration time (e.g., 1 hour)
        cache.set('overdue_emprunts', overdue_emprunts, timeout=3600)

    def __call__(self, request):
        # Check if the overdue emprunts are cached
        overdue_emprunts = cache.get('overdue_emprunts')

        if overdue_emprunts is None:
            self.update_overdue_emprunts_cache()

        # Call the next middleware or view
        response = self.get_response(request)
        return response

@receiver(post_save, sender=Emprunter)
def handle_emprunter_update(sender, instance, created, **kwargs):
    # Update overdue emprunts cache when Emprunter model is updated
    middleware = UpdateOverdueEmpruntsCacheMiddleware()
    middleware.update_overdue_emprunts_cache()

class DeleteOldReservationsMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def delete_old_reservations(self):
        today_date = timezone.now().date()
        old_reservations = Reservation.objects.filter(date_emprunt__lt=today_date)
        deleted_count, _ = old_reservations.delete()
        logger.info(f'Deleted {deleted_count} old reservations.')

    def __call__(self, request):
        self.delete_old_reservations()
        response = self.get_response(request)
        return response