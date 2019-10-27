import copy

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.ProceedingStage import (
    ProceedingStage,
)
from src.cs_models.resources.ProceedingStage.models import (
    ProceedingStageModel,
)
from src.cs_models.resources.PTAB2Proceeding import PTAB2Proceeding
from src.cs_models.database import db_session


class ProceedingStageResourceTestCase(TestCase):
    def setUp(self):
        super(ProceedingStageResourceTestCase, self).setUp()
        self.inst = ProceedingStage()
        self.inst_ptab2_proceeding = PTAB2Proceeding()

        self.ptab2_proceeding1 = self.inst_ptab2_proceeding.create({
            'accorded_filing_date': '05-06-2013',
            'decision_date': '10-07-2014',
            'institution_decision_date': '10-08-2013',
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Steven Baughman',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'Apple Inc.',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_filing_date': '05-06-2013',
            'proceeding_last_modified_date': '-',
            'proceeding_number': 'IPR-100',
            'proceeding_status_category': 'FWD Entered',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '08471964',
            'respondent_counsel_name': 'David Marsh',
            'respondent_grant_date': '10-12-1999',
            'respondent_group_art_unit_number': '-',
            'respondent_inventor_name': 'ARTHUR HAIR',
            'respondent_party_name': 'SightSound Technologies LLC',
            'respondent_patent_number': '5966440',
            'respondent_patent_owner_name': 'SightSound Technologies LLC',
            'respondent_technology_center_number': '2100',
            'subproceeding_type_category': 'CBM',
            'company_id': None,
        })

        self.proceeding_stage1 = self.inst.create({
            'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
            'stage': 'Petition Filed',
            'is_active': True,
            'filed_date': '06/11/2019',
            'due_date': None,
        })

        self.valid_data = {
            'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
            'stage': 'PO Preliminary Response',
            'is_active': True,
            'filed_date': '06/11/2019',
            'due_date': '06/20/2019',
        }

    @parameterized.expand([
        ('ptab2_proceeding_id',),
        ('stage',),
        ('is_active',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            base_data,
        )

    def test_create_violates_unique_constraint(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {
                'ptab2_proceeding_id': (
                    self.proceeding_stage1['ptab2_proceeding_id']),
                'stage': self.proceeding_stage1['stage'],
                'is_active': True,
            },
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(
            self.valid_data,
            resp,
            fields_to_ignore=['filed_date', 'due_date'],
        )

    def test_delete(self):
        self.inst.delete(id=self.proceeding_stage1['id'])

        q = self._build_query(proceeding_stage_id=self.proceeding_stage1['id'])

        assert q.first() is None

    @staticmethod
    def _build_query(proceeding_stage_id: int) -> Query:
        q = db_session.query(
            ProceedingStageModel,
        ).filter_by(id=proceeding_stage_id)
        return q

