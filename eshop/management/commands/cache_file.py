from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = "Clear all the cache"

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(self.style.SUCCESS("Successfully delete all the cache"))