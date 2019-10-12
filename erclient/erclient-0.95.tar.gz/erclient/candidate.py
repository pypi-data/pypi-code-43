from os.path import basename
import datetime
from io import BufferedReader

from .address import get_address_type_id_by_name, get_address_state_id_by_name, get_address_region_id_by_name, \
    list_addresses, get_address_by_id, add_address
from .base import ErConnector
from .communication import list_communication_methods, add_communication_method, list_communication_categories
from .config import rest_entity_id
from .customfield import get_remote_customfield_list_for_abouttype, get_remote_customfield_list_for_abouttype_record, \
    get_custom_field_by_key
from .owner import get_owners, get_primary_owner
from .seed import create_seed, get_seed_type_id_by_name, update_seed


class Candidate(object):

    def __init__(self, candidate_id, data=None):
        self.candidate_id = candidate_id
        if data:
            #allows obj to be populated by another call that returns a candidate record, eg duplicate/
            self.data = data
        else:
            self.data = get_remote_candidate(candidate_id)

    def __str__(self):
        return self.full_name()

    def first_name(self):
        return '{first}'.format(
            first=self.data.get('First', None),
        )

    def last_name(self):
        return '{last}'.format(
            last=self.data.get('Last', None)
        )

    def full_name(self):
        return '{first} {last}'.format(
            first=self.first_name(),
            last=self.last_name(),
        )

    def email_address(self, as_obj=False):
        obj = get_candidate_primary_email_address(self.candidate_id)
        if as_obj:
            return obj
        else:
            return obj.value

    def fetch(self):
        self.data = get_remote_candidate(self.candidate_id)

    def list_communication_methods(self, about_id=None, is_primary=False):
        return list_candidate_communication_methods(self.candidate_id, about_id=about_id, is_primary=is_primary)

    def add_communication_method(self, category_id, value, is_primary=False):
        return add_communication_method(
            abouttype_id='Candidate',
            type_id=category_id,
            obj_id=self.candidate_id,
            value=value,
            is_primary=is_primary
        )

    def list_email_addresses(self, as_obj=False):
        # default is to return just the list of addresses, not the object. Returning obj is optional
        obj_list = list_candidate_email_addresses(self.candidate_id)
        if as_obj:
            return obj_list
        else:
            return [x.value for x in obj_list]

    def upload_and_parse_resume(self, resume, with_copy=True):
        return upload_and_parse_resume(self.candidate_id, resume, with_copy=with_copy)

    def add_note(self, body, action_id=0):
        return add_note_to_candidate(self.candidate_id, body, action_id)

    def get_communication_preferences(self, type=None):
        connector = ErConnector()  # 2.0 API
        url = 'Candidate/{id}/CommunicationPreferences'.format(
            type=type,
            id=self.candidate_id
        )
        response = connector.send_request(
            path=url,
            verb='GET',
        )

        return response

    def set_communication_preferences(self, pref_dict):
        connector = ErConnector()  # 2.0 API
        url = 'Candidate/{id}/CommunicationPreferences'.format(
            id=self.candidate_id
        )

        payload = self.get_communication_preferences()
        for x in pref_dict.keys():
            payload[x] = pref_dict[x]

        response = connector.send_request(
            path=url,
            verb='POST',
            payload=payload
        )

        return response

    def list_custom_fields(self):
        return get_remote_customfield_list_for_abouttype_record('Candidate', obj_id=self.candidate_id)

    def get_custom_field(self, key, value_only=False):
        return get_custom_field_by_key('Candidate', key, self.candidate_id, value_only=value_only)

    def get_custom_field_value(self, key):
        return self.get_custom_field(key, value_only=True)

    def save_custom_field_value(self, key, value):
        field = self.get_custom_field(key)
        return field.set_value(value, obj_id=self.candidate_id, save=True)

    def list_references(self):
        return list_candidate_references(self.candidate_id)

    def do_not_email(self):
        return self.get_communication_preferences()['DoNotEmail']

    def do_not_call(self):
        return self.get_communication_preferences()['DoNotCall']

    def do_not_text(self):
        return self.get_communication_preferences()['DoNotText']

    def set_do_not_email_true(self):
        return self.set_communication_preferences({'DoNotEmail': True})

    def set_do_not_email_false(self):
        return self.set_communication_preferences({'DoNotEmail': False})

    def get_owners(self):
        return get_owners('Candidate', self.candidate_id)

    def get_recruiter(self):
        return get_primary_owner('Candidate', self.candidate_id)

    def get_recruiter_name(self):
        return self.get_recruiter().full_name

    def get_rating(self):
        response = get_candidate_rating(self.candidate_id)
        try:
            return response
        except:
            return None

    def get_address(self):
        return get_address_by_id(self.data.get('DefaultAddressID', None))

    def add_address(self, type_id, address_line_1, city, state_id, region_id, postal_code):
        result =  add_address(
            abouttype_id='Candidate',
            type_id=type_id,
            obj_id=self.candidate_id,
            address_line_1=address_line_1,
            city=city,
            state_id=state_id,
            region_id=region_id,
            postal_code=postal_code,

        )
        return result

    def add_contact_reference(self,
                              first_name,
                              last_name,
                              title=None,
                              company_name=None,
                              adsource_id=None,
                              phone=None,
                              email=None,
                              address=None,
                              city=None,
                              state=None,
                              postal_code=None,
                              reference_type=None,
                              reference_text=None,
                              relationship_start_date=None,
                              relationship_end_date=None,
                              rating=None
                              ):
        if not adsource_id:
            adsource_id = 228
        if not reference_type:
            reference_type = 90
        if not rating:
            rating = self.get_rating() or get_candidate_rating_id_by_name('A')

        seed = (
            create_seed(
                type_id=get_seed_type_id_by_name('Reference'),
                expected_harvest_type='Contact',
                adsource_id=adsource_id,
                assign_to=self.get_recruiter().user_id,
                first_name=first_name,
                last_name=last_name,
                title=title,
                company_name=company_name
            )
        )

        # because company_name doesnt seem to save correctly for the creation method

        if company_name:
            update_seed(seed.seed_id, CompanyName=company_name)

        if email:
            seed.add_communication_method(type_id=200, value=email, is_primary=True)

        if phone:
            seed.add_communication_method(type_id=100, value=phone, is_primary=True)
        if address:
            type_id = get_address_type_id_by_name('Main Address')
            seed.add_address(
                type_id=type_id,
                address_line_1=address,
                city=city,
                state_id=get_address_state_id_by_name(state),
                region_id=get_address_region_id_by_name('Metro DC'),
                postal_code=postal_code
            )

        try:
            relationship_start_date = relationship_start_date.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            relationship_start_date = None
        try:
            relationship_end_date = relationship_end_date.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            relationship_end_date = None

        response = add_candidate_reference(
            candidate_id=self.candidate_id,
            reference_type=reference_type,
            reference_id=seed.seed_id,
            reference_text=reference_text,
            name='Reference from {name}'.format(name=seed.full_name),
            relationship_start_date=relationship_start_date,
            relationship_end_date=relationship_end_date,
            rating=rating
        )

        return CandidateReference(candidate_id=self.candidate_id, reference_id=response['ID'], data=response,
                                  candidate=self)


class CandidateReference(object):

    def __init__(self, candidate_id, reference_id, data=None, candidate=None):

        self.candidate_id = candidate_id
        self.reference_id = reference_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            self.data = data
            # self.refresh(fetch=False)
        self.populate_from_data()
        if not candidate:
            self.candidate = Candidate(self.candidate_id)
        else:
            self.candidate = candidate

    def refresh(self):
        self.data = get_candidate_reference_by_id(self.candidate_id, self.reference_id)
        self.populate_from_data()

    def populate_from_data(self):
        self.reference_type = self.data['ReferenceType']
        self.name = self.data['Name']
        self.entered_on = self.data['EnteredOn']
        try:
            self.relationship_start_date = datetime.datetime.strptime(self.data['RelationshipStartDate'],
                                                                      '%Y-%m-%dT%H:%M:%S')
        except:
            self.relationship_start_date = None
        try:
            self.relationship_end_date = datetime.datetime.strptime(self.data['RelationshipEndDate'],
                                                                    '%Y-%m-%dT%H:%M:%S')
        except:
            self.relationship_end_date = None
        self.reference_text = get_candidate_reference_text_by_reference_id(self.reference_id)


class CandidateReferenceImportSet(object):
    def __init__(self, candidate, references):
        self.candidate = candidate
        self.references = references


def list_candidate_references(candidate_id):
    # API 2.0
    connector = ErConnector()
    url = 'CandidateReference/{candidate_id}/'.format(candidate_id=candidate_id)
    response = connector.send_request(
        path=url
    )
    return [CandidateReference(candidate_id=reference['CandidateID'], reference_id=reference['ID'], data=reference) for
            reference in response]


def get_candidate_reference_by_id(candidate_id, reference_id):
    # API 2.0
    try:
        return \
            [reference for reference in list_candidate_references(candidate_id) if
             reference.reference_id == reference_id][
                0]
    except:
        return None


def add_candidate_reference(candidate_id, reference_type, reference_id, reference_text, name,
                            relationship_start_date=None, relationship_end_date=None, rating=0):
    # API 2.0
    connector = ErConnector()
    url = '/CandidateReference/'
    data = {}
    data['CandidateID'] = candidate_id
    data['ReferenceType'] = reference_type  # ie "Seed"
    data['ReferenceID'] = reference_id  # id of the Seed
    data['ReferenceText'] = reference_text
    data['Name'] = name
    data['RelationshipStartDate'] = relationship_start_date
    data['RelationshipEndDate'] = relationship_end_date
    data['Rating'] = rating
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )

    return response


def get_candidate_reference_text_by_reference_id(reference_id):
    # API 2.0
    connector = ErConnector()
    url = '/CandidateReference/{Id}/Text'.format(Id=reference_id)
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    try:
        return response['Text']
    except:
        return None


def candidate_schema(schema):
    schema.pop('_expanded', None)
    schema.pop('_links', None)
    return schema


def list_candidate_custom_fields(indexonly=False):
    return get_remote_customfield_list_for_abouttype('Candidate')


def get_remote_candidate(candidate_id):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/{candidate_id}/'.format(candidate_id=candidate_id)
    response = connector.send_request(
        path=url
    )
    return response


def list_candidate_communication_methods(candidate_id, about_id=None, is_primary=False):
    # API 2.0
    return list_communication_methods('Candidate', candidate_id, about_id=about_id, is_primary=is_primary)


def list_candidate_email_addresses(candidate_id):
    # API 2.0
    return list_candidate_communication_methods(candidate_id, about_id=200)


def list_candidate_addresses(candidate_id):
    # API 2.0
    return list_addresses('Candidate', candidate_id)


def get_candidate_primary_email_address(candidate_id):
    # API 2.0
    try:
        return [x for x in list_candidate_email_addresses(candidate_id) if x.is_primary][0]
    except:
        return None


def get_candidate_rating(candidate_id):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/Rating/{candidate_id}/'.format(candidate_id=candidate_id)
    response = connector.send_request(
        path=url
    )
    try:
        return get_candidate_rating_name_by_id(response['ID'])
    except:
        return None


def list_candidate_ratings():
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/Rating/'
    response = connector.send_request(
        path=url
    )
    return response


def get_candidate_rating_id_by_name(name):
    # API 2.0
    try:
        return [x for x in list_candidate_ratings() if x['Name'] == name][0]['ID']
    except:
        return None


def get_candidate_rating_name_by_id(id):
    # API 2.0
    try:
        return [x for x in list_candidate_ratings() if x['ID'] == id][0]['Name']
    except:
        return None


def add_note_to_candidate(candidate_id, body, action_id=0):
    # using REST API
    connector = ErConnector(api_version='rest')
    path = 'Candidate/{entityid}/{candidate_id}/AddNote?ActionID={action_id}'.format(
        entityid=connector.rest_entity_id,
        candidate_id=candidate_id,
        action_id=action_id
    )
    params = {}
    params['CreatedByID'] = connector.api_user_guid_rest
    params['Body'] = body
    params['ActionID'] = action_id
    return connector.send_request(
        path,
        payload=params,
        verb='POST',
    )['Data']['Message']


def upload_attachment_to_candidate_profile(candidate_id, file, type_id):
    # using REST uploader
    connector = ErConnector(api_version='rest')
    path = 'Attachment/Do/UploadAttachment/'
    try:
        name = basename(file)
    except TypeError:
        name = basename(file.name)
    params = {}
    params['ReferenceID'] = candidate_id
    params['CreatedByID'] = connector.api_user_guid_rest
    params['AttachmentTypeID'] = type_id
    params['Name'] = name
    params['AboutTypeID'] = 6
    params['EntityID'] = rest_entity_id
    files = {}
    files['file'] = file
    return connector.send_request(
        path,
        payload=params,
        file=file,
        verb='POST',
    )['Data']['Message']


def upload_resume_to_candidate_profile(candidate_id, file):
    # Use 1.0 attachment uploader for resume and return attachment_id
    connector = ErConnector(api_version='rest')
    path = 'Candidate/{EntityID}/{CandidateID}/UploadResume/'.format(
        EntityID=rest_entity_id,
        CandidateID=candidate_id,
        CreatorGUID=connector.api_user_guid_rest
    )
    params = {}
    params['ChangedByID'] = connector.api_user_guid_rest
    params['CreatedByID'] = connector.api_user_guid_rest
    params['IsDefaultResume'] = True
    params['ParseSkills'] = True
    params['ReplaceSkills'] = False
    files = {}
    # files['file'] = file
    return connector.send_request(
        path,
        payload=params,
        file=file,
        verb='POST',
    )['Data']['Message']


def import_resume_from_attachment(
        candidate_id,
        attachment_id,
        replace_contact_info=True,
        update_employment='Update',
        update_education='Update',
        update_skills='Update'

):
    # Use 2.0 parser on an existing attachment
    path = '/Candidate/{Id}/Resume/Attachment/{AttachmentID}/?replaceContactInfo={replace_contact_info}' \
           '&updateEmployment={update_employment}&updateEducation={update_education}&updateSkills={update_skills}' \
        .format(
        Id=candidate_id,
        AttachmentID=attachment_id,
        replace_contact_info=str(replace_contact_info),
        update_employment=update_employment,
        update_education=update_education,
        update_skills=update_skills
    )
    connector = ErConnector()
    payload = {
        'replaceContactInfo': replace_contact_info,
        'updateEmployment': update_employment,
        'updateEducation': update_education,
        'updateSkills': update_skills

    }

    response = connector.send_request(
        path=path,
        payload=payload,
        verb='PUT',
    )
    return response


def upload_and_parse_resume(candidate_id, file, with_copy=False):
    # A helper method that uploads a resume, sets it to the default resume, parses it using the new parser,
    # optionally uploads a copy that has the same filename as the uploaded file as its name. This is because any
    # file uploaded using the "Resume" method is renamed "Resume" by the API regardless of the filename.
    if not (isinstance(file, BufferedReader)):
        raise Exception('Error: File must be in BufferedReader format')
    else:
        attachments = []
        attachment_id = upload_resume_to_candidate_profile(candidate_id, file)
        attachments.append(attachment_id)
        parse_result = import_resume_from_attachment(candidate_id, attachment_id)
        if with_copy:
            attachment_id = upload_attachment_to_candidate_profile(candidate_id, file, type_id=1)
            attachments.append(attachment_id)
        return attachments

def list_duplicates(first=None, last=None, middle=None, emails=None, phones=None):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/Duplicate'
    payload = {
        'First':first,
        'Last':last,
        'Middle': middle,
        'Emails':emails,
        'Phones':phones,
    }
    response = connector.send_request(
        path=url,
        payload=payload,
        verb='POST'
    )
    return [Candidate(candidate_id=can['ID'], data=can) for can in response]

def create_candidate(
        first,
        last,
        title,
        folder_group_id,
        adsource_id,
        emails,
        phones,
        ad_source_additional_info=None,
        middle=None,
        ssn=None):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/'

    payload = {
        'First':first,
        'Last':last,
        'Middle':middle,
        'Title':title,
        'FolderGroupID':folder_group_id,
        'AdSourceID':adsource_id,
        'AdSourceAdditionalInfo':ad_source_additional_info,
        'Emails':emails,
        'Phones':phones,
        'SSN':ssn
    }
    response = connector.send_request(
        path=url,
        payload=payload,
        verb='POST'
    )
    try:
        return Candidate(candidate_id=response['ID'], data=response)
    except:
        return response
