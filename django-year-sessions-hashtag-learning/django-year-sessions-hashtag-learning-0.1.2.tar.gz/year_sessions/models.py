from django.db import models

YEARS_TO_EXCLUDE = ['2018-19']

class YearSessionManager(models.Manager):

    def get_session_from_string(self, session_as_string):
        return self.get(
            session=session_as_string
        )

    def get_session(self, pk):
        return self.get(
            pk=pk
        )

    def get_n_sessions(self, start_session, number_of_sessions):
        return self.all(
        ).filter(pk__gte=start_session.pk).order_by('pk')[0:number_of_sessions]

    def get_year_sessions_excluding_those_passed(self):

        return self.all(
        ).exclude(
            session__in=YEARS_TO_EXCLUDE
        ).order_by('pk')



class YearSession(models.Model):
    session = models.CharField(max_length=10, default='2017-18')

    objects = YearSessionManager()

    def __str__(self):
        return self.session

