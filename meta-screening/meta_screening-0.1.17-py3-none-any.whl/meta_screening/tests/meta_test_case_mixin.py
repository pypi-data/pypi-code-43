from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import YES
from edc_facility.import_holidays import import_holidays
from edc_facility.models import Holiday
from edc_list_data.site_list_data import site_list_data
from edc_randomization.models.randomization_list import RandomizationList
from edc_randomization.randomization_list_importer import RandomizationListImporter
from edc_sites.tests.site_test_case_mixin import SiteTestCaseMixin
from edc_utils.date import get_utcnow
from meta_sites.sites import fqdn, meta_sites
from model_mommy import mommy

from ..models import (
    ScreeningPartOne,
    ScreeningPartTwo,
    ScreeningPartThree,
    SubjectScreening,
)
from .options import (
    part_one_eligible_options,
    part_two_eligible_options,
    part_three_eligible_options,
)


class MetaTestCaseMixin(SiteTestCaseMixin):

    fqdn = fqdn

    default_sites = meta_sites

    site_names = [s[1] for s in default_sites]

    import_randomization_list = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.import_randomization_list:
            RandomizationListImporter(verbose=False)
        import_holidays(test=True)
        site_list_data.autodiscover()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        RandomizationList.objects.all().delete()
        Holiday.objects.all().delete()

    def get_subject_screening(self):
        part_one = ScreeningPartOne.objects.create(
            user_created="erikvw", user_modified="erikvw", **part_one_eligible_options
        )
        screening_identifier = part_one.screening_identifier
        self.assertEqual(part_one.eligible_part_one, YES)

        screening_part_two = ScreeningPartTwo.objects.get(
            screening_identifier=screening_identifier
        )
        for k, v in part_two_eligible_options.items():
            setattr(screening_part_two, k, v)
        screening_part_two.save()
        print(screening_part_two.reasons_ineligible_part_two)
        self.assertEqual(screening_part_two.eligible_part_two, YES)

        screening_part_three = ScreeningPartThree.objects.get(
            screening_identifier=screening_identifier
        )
        for k, v in part_three_eligible_options.items():
            setattr(screening_part_three, k, v)
        screening_part_three.save()
        self.assertEqual(screening_part_three.eligible_part_three, YES)

        subject_screening = SubjectScreening.objects.get(
            screening_identifier=screening_identifier
        )
        self.assertTrue(subject_screening.eligible)
        return subject_screening

    def get_subject_consent(self, subject_screening):
        return mommy.make_recipe(
            "meta_consent.subjectconsent",
            user_created="erikvw",
            user_modified="erikvw",
            screening_identifier=subject_screening.screening_identifier,
            initials=subject_screening.initials,
            dob=get_utcnow().date()
            - relativedelta(years=subject_screening.age_in_years),
            site=Site.objects.get(name="hindu_mandal"),
        )
