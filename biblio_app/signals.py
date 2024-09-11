
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Ouvrage, Reservation

@receiver(post_save, sender=Reservation)
def handle_reservation_update(sender, instance, created, **kwargs):
    today_date = timezone.now().date()
    
    # Fetch old reservations once
    old_reservations = Reservation.objects.filter(date_emprunt__lt=today_date)
    
    ouvrages_to_update = {}
    
    for reservation in old_reservations:
        ouvrage = reservation.ouvrage
        if ouvrage not in ouvrages_to_update:
            ouvrages_to_update[ouvrage] = 0
        ouvrages_to_update[ouvrage] += 1
    
    # Update all ouvrages in bulk
    for ouvrage, increment in ouvrages_to_update.items():
        ouvrage.num_exmp_dispo += increment
        ouvrage.save()
    
    # Delete all old reservations in one query
    old_reservations.delete()
