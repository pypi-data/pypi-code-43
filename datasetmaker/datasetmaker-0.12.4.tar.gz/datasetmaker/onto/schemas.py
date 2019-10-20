from cerberus import schema_registry
from datasetmaker.onto.manager import read_entity

_cache: dict = dict()


def _allow(name: str) -> list:
    return _cache.get(name, read_entity(name)[name].to_list())


schema_registry.add('country', {
    'country': {'type': 'string', 'allowed': _allow('country')},
    'name': {'type': 'string'},
    'iso3': {'type': 'string', 'nullable': True},
    'iso2': {'type': 'string', 'nullable': True},
    'un_state': {'type': 'boolean'},
    'region4': {'type': 'string', 'allowed': _allow('region4'), 'nullable': True},
    'region6': {'type': 'string', 'allowed': _allow('region6'), 'nullable': True},
    'slug': {'type': 'string'},
    'landlocked': {'type': 'boolean'}
})

schema_registry.add('region4', {
    'region4': {'type': 'string', 'allowed': _allow('region4')},
    'name': {'type': 'string'},
    'slug': {'type': 'string'},
})

schema_registry.add('region6', {
    'region6': {'type': 'string', 'allowed': _allow('region6')},
    'name': {'type': 'string'},
    'slug': {'type': 'string'},
})

schema_registry.add('gender', {
    'gender': {'type': 'string', 'allowed': _allow('gender')},
    'name': {'type': 'string'},
    'slug': {'type': 'string'},
})

schema_registry.add('person', {
    'person': {'type': 'string'},
    # 'name': {'type': 'string'},
    'first_name': {'type': 'string'},
    'last_name': {'type': 'string'},
    'birth.day': {'type': 'date'},
    'birth.city': {'type': 'string'},
    'birth.country': {'type': 'string', 'allowed': _allow('country')},
    'death.day': {'type': 'date'},
    'death.city': {'type': 'string'},
    'death.country': {'type': 'string', 'allowed': _allow('country')},
})

schema_registry.add('city', {
    'city': {'type': 'string'},
    'name': {'type': 'string'},
    'country': {'type': 'string', 'allowed': _allow('country'), 'nullable': True},
})

schema_registry.add('nobel_laureate', {
    'nobel_laureate': {'type': 'string'},
    'first_name': {'type': 'string'},
    'last_name': {'type': 'string', 'nullable': True},
    'birth.day': {'type': 'date', 'nullable': True},
    'birth.city': {'type': 'string', 'nullable': True},
    'birth.country': {'type': 'string', 'allowed': _allow('country'), 'nullable': True},
    'death.day': {'type': 'date', 'nullable': True},
    'death.city': {'type': 'string', 'nullable': True},
    'death.country': {'type': 'string', 'allowed': _allow('country'), 'nullable': True},
})

schema_registry.add('nobel_category', {
    'nobel_category': {'type': 'string', 'allowed': _allow('nobel_category')},
    'name': {'type': 'string'}
})

schema_registry.add('nobel_prize', {
    'nobel_prize': {'type': 'string'},
    'nobel_laureate': {'type': 'string'},
    'nobel_category': {'type': 'string', 'allowed': _allow('nobel_category')},
    'nobel_motivation': {'type': 'string'},
    'year': {'type': 'integer', 'min': 1901}
})

schema_registry.add('nobel_instance', {
    'nobel_instance': {'type': 'string'},
    'nobel_category': {'type': 'string', 'allowed': _allow('nobel_category')},
    'year': {'type': 'integer', 'min': 1901}
})

schema_registry.add('pollster', {
    'pollster': {'type': 'string'},
    'name': {'type': 'string'},
    'valforsk_pollster_link': {'type': 'string'},
    'valforsk_in_mama': {'type': 'boolean'},
    'valforsk_mode': {'type': 'string'},
})

schema_registry.add('party', {
    'party': {'type': 'string', 'allowed': _allow('party')},
    'name': {'type': 'string'},
    'abbr': {'type': 'string'},
    'country': {'type': 'string', 'allowed': _allow('country'), 'nullable': True, 'empty': True},
    'slug': {'type': 'string'},
})

schema_registry.add('unsc_sanctioned_entity', {
    'unsc_sanctioned_entity': {'type': 'string'},
    'unsc_versionnum': {'type': 'string'},
    'unsc_first_name': {'type': 'string'},
    'unsc_un_list_type': {'type': 'string'},
    'unsc_reference_number': {'type': 'string'},
    'unsc_listed_on': {'type': 'string'},
    'unsc_comments1': {'type': 'string', 'empty': True, 'nullable': True},
    'unsc_name_original_script': {'type': 'string', 'empty': True, 'nullable': True},
    'unsc_submitted_on': {'type': 'string', 'empty': True, 'nullable': True},
})

schema_registry.add('unsc_sanctioned_individual', {
    'unsc_sanctioned_individual': {'type': 'string'},
    'unsc_versionnum': {'type': 'string'},
    'unsc_first_name': {'type': 'string'},
    'unsc_second_name': {'type': 'string', 'empty': True, 'nullable': True},
    'unsc_third_name': {'type': 'string', 'empty': True, 'nullable': True},
    'unsc_un_list_type': {'type': 'string'},
    'unsc_reference_number': {'type': 'string'},
    'unsc_listed_on': {'type': 'string'},
    'unsc_comments1': {'type': 'string', 'empty': True, 'nullable': True},
    'unsc_name_original_script': {'type': 'string', 'empty': True, 'nullable': True},
    'unsc_fourth_name': {'type': 'string', 'empty': True, 'nullable': True},
    'gender': {'type': 'string', 'allowed': _allow('gender'), 'empty': True, 'nullable': True},
    'unsc_submitted_by': {'type': 'string', 'empty': True, 'nullable': True}
})

schema_registry.add('esv_expenditure', {
    'esv_expenditure': {'type': 'string'},
    'name': {'type': 'string'}
})

schema_registry.add('esv_allocation', {
    'esv_allocation': {'type': 'string'},
    'name': {'type': 'string'}
})

schema_registry.add('sipri_currency', {
    'sipri_currency': {'type': 'string'}
})

schema_registry.add('head_gov', {
    'head_gov': {'type': 'string'},
    'name': {'type': 'string'},
    'title': {'type': 'string'},
})

schema_registry.add('head_state', {
    'head_state': {'type': 'string'},
    'name': {'type': 'string'},
    'title': {'type': 'string'}
})

schema_registry.add('election', {
    'election': {'type': 'string'},
    'country': {'type': 'string'},
    'day': {'type': 'string'},
    'type': {'type': 'string', 'allowed': ['parliamentary', 'presidential']},
})

schema_registry.add('meps_political_group', {
    'meps_political_group': {'type': 'string'}
})

schema_registry.add('meps_national_political_group', {
    'meps_national_political_group': {'type': 'string'}
})

schema_registry.add('meps_mep', {
    'meps_mep': {'type': 'string'},
    'first_name': {'type': 'string'},
    'last_name': {'type': 'string'},
    'meps_political_group': {'type': 'string'},
    'meps_national_political_group': {'type': 'string'}
})

schema_registry.add('aggregation_method', {
    'aggregation_method': {'type': 'string'},
    'name': {'type': 'string'}
})

schema_registry.add('source', {
    'source': {'type': 'string'},
    'name': {'type': 'string'},
    'slug': {'type': 'string'}
})

schema_registry.add('topic', {
    'topic': {'type': 'string'},
    'name': {'type': 'string'},
    'slug': {'type': 'string'},
    'parent_topic': {'type': 'string'},
    'country': {'type': 'string', 'empty': True, 'allowed': _allow('country')},
})

schema_registry.add('locale', {
    'locale': {'type': 'string'},
    'name': {'type': 'string'},
    'name_english': {'type': 'string'}
})

schema_registry.add('synonym_type', {
    'synonym_type': {'type': 'string'},
    'name': {'type': 'string'}
})

schema_registry.add('jurisdiction', {
    'jurisdiction': {'type': 'string'},
    'name': {'type': 'string'}
})

schema_registry.add('visa_requirement', {
    'visa_requirement': {'type': 'string'},
    'name': {'type': 'string'}
})

schema_registry.add('media_org', {
    'media_org': {'type': 'string'},
    'name': {'type': 'string'},
})

schema_registry.add('mynewsflash_swe_media_country_mention', {
    'mynewsflash_swe_media_country_mention': {'type': 'string'},
    'country': {'type': 'string', 'allowed': _allow('country')},
    'day': {'type': 'string'},
    'headline': {'type': 'string'},
    'media_org': {'type': 'string', 'allowed': _allow('media_org')},
    'url': {'type': 'string'},
})

schema_registry.add('valforsk_issue', {
    'valforsk_issue': {'type': 'string'},
    'name': {'type': 'string'},
    'valforsk_source': {'type': 'string'},
})

schema_registry.add('scb_psu_pop_segment', {
    'scb_psu_pop_segment': {'type': 'string'},
    'name': {'type': 'string'},
    'sname': {'type': 'string'},
})

# schema_registry.add('huvudman', {
#     'huvudman': {'type': 'string'},
#     'name': {'type': 'string'},
#     'type': {'type': 'string'},
# })

schema_registry.add('municipality', {
    'municipality': {'type': 'string'},
    'name': {'type': 'string'},
    'country': {'type': 'string', 'allowed': _allow('country')},
})

schema_registry.add('skolverket_school_subject', {
    'skolverket_school_subject': {'type': 'string'},
})

schema_registry.add('skolverket_delprov_tcv49', {
    'skolverket_delprov_tcv49': {'type': 'string'},
})

schema_registry.add('skolverket_provnamn', {
    'skolverket_provnamn': {'type': 'string'},
})

schema_registry.add('skolverket_program', {
    'skolverket_program': {'type': 'string'},
})

schema_registry.add('skolverket_prov', {
    'skolverket_prov': {'type': 'string'},
})

schema_registry.add('skolverket_provkod', {
    'skolverket_provkod': {'type': 'string'},
})

schema_registry.add('skolverket_semester', {
    'skolverket_semester': {'type': 'string'},
})

schema_registry.add('skolverket_inriktning_tcv70', {
    'skolverket_inriktning_tcv70': {'type': 'string'},
})

schema_registry.add('skolverket_inriktning', {
    'skolverket_inriktning': {'type': 'string'},
})

schema_registry.add('skolverket_provkod_tcv193', {
    'skolverket_provkod_tcv193': {'type': 'string'},
})

schema_registry.add('skolverket_provnamn_tcv193', {
    'skolverket_provnamn_tcv193': {'type': 'string'},
})

schema_registry.add('skolverket_provnamn_tcv12', {
    'skolverket_provnamn_tcv12': {'type': 'string'},
})

schema_registry.add('skolverket_delprovsnamn_tcv12', {
    'skolverket_delprovsnamn_tcv12': {'type': 'string'},
})

schema_registry.add('skolverket_delprovsnamn', {
    'skolverket_delprovsnamn': {'type': 'string'},
})

schema_registry.add('school_unit', {
    'school_unit': {'type': 'string'},
    'name': {'type': 'string', 'nullable': True},
    'huvudman': {'type': 'string', 'nullable': True},
    'huvudman_type': {'type': 'string', 'nullable': True},
    'municipality': {'type': 'string', 'nullable': True, 'allowed': _allow('municipality')},
    'lat': {'type': 'float', 'nullable': True},
    'lng': {'type': 'float', 'nullable': True},
    'url': {'type': 'string', 'nullable': True},
})
