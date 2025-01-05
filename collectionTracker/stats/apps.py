from django.apps import AppConfig

class StatsConfig(AppConfig):
    name = 'stats'

    def ready(self):
        import stats.signals
        # Remove the call to create_all_badges to avoid database access during app initialization
        # from stats.signals import create_all_badges
        # create_all_badges()
