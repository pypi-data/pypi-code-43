from django.test import TestCase, tag

from meta_screening.tests.meta_test_case_mixin import MetaTestCaseMixin

from meta_visit_schedule.constants import DAY1
from edc_pharmacy.constants import IN_PROGRESS_APPT
from edc_appointment.models import Appointment
from edc_visit_tracking.constants import SCHEDULED
from meta_lists.models import (
    BaselineSymptoms,
    ArvRegimens,
    OiProphylaxis,
    DiabetesSymptoms,
)

from ..models import SubjectVisit
from ..forms import PatientHistoryForm
from pprint import pprint
from edc_constants.constants import YES, NO, NOT_APPLICABLE, OTHER
from edc_utils.date import get_utcnow

options = {
    "current_arv_regimen": None,
    "current_smoker": YES,
    "dia_blood_pressure": 80,
    "family_diabetics": NO,
    "former_smoker": NOT_APPLICABLE,
    "has_abdominal_tenderness": NO,
    "has_enlarged_liver": NO,
    "has_previous_arv_regimen": NO,
    "heart_rate": 65,
    "hypertension": YES,
    "is_heartbeat_regular": YES,
    "jaundice": YES,
    "oi_prophylaxis": None,
    "on_hypertension_treatment": YES,
    "on_oi_prophylaxis": YES,
    "past_year_symptoms": None,
    "peripheral_oedema": YES,
    "previous_arv_regimen": None,
    "report_datetime": get_utcnow(),
    "respiratory_rate": 12,
    "statins": YES,
    "symptoms": None,
    "sys_blood_pressure": 120,
    "temperature": 37,
    "waist_circumference": 61,
    "weight": 65,
}


class TestPatientHistory(MetaTestCaseMixin, TestCase):
    def test_(self):
        subject_screening = self.get_subject_screening()
        subject_consent = self.get_subject_consent(subject_screening)
        subject_identifier = subject_consent.subject_identifier

        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier, visit_code=DAY1
        )
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )

        symptoms = BaselineSymptoms.objects.filter(short_name=OTHER)
        arv_regimens = ArvRegimens.objects.filter(short_name="TDF_3TC_ATV_r")
        oi_prophylaxis = OiProphylaxis.objects.filter(
            short_name__in=["nausea", "weakness"]
        )
        diabetes_symptoms = DiabetesSymptoms.objects.all()

        data = {k: v for k, v in options.items()}
        data.update(
            subject_visit=subject_visit.pk,
            symptoms=symptoms,
            current_arv_regimen=arv_regimens,
            previous_arv_regimen=[],
            oi_prophylaxis=oi_prophylaxis,
            diabetes_symptoms=diabetes_symptoms,
        )

        form = PatientHistoryForm(data=data)
        form.is_valid()
        pprint(form._errors)
