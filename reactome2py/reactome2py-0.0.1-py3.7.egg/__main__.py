from __future__ import print_function
from __future__ import unicode_literals
import argparse
from . import analysis
from . import content


def testing():
    print('yay')


def build_parser():
    """
    Builds the user-input arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Interfaces with reactome2py.')

    subparsers = parser.add_subparsers(title='commands',
                                       description='The following commands are available:',
                                       help='For additional help: "reactome2py <COMMAND> -h"')

    # analysis services -------------------------------------------------
    parser_identifier = subparsers.add_parser('identifier', help='')
    parser_identifier.add_argument('--ids', help='', required=False, type=str)
    parser_identifier.add_argument('--interactors', help='', required=False, type=bool)
    parser_identifier.add_argument('--page_size', help='', required=False, type=str)
    parser_identifier.add_argument('--page', help='', required=False, type=str)
    parser_identifier.add_argument('--species', help='', required=False, type=str)
    parser_identifier.add_argument('--sort_by', help='', required=False, type=str)
    parser_identifier.add_argument('--order', help='', required=False, type=str)
    parser_identifier.add_argument('--resource', help='', required=False, type=str)
    parser_identifier.add_argument('--p_value', help='', required=False, type=str)
    parser_identifier.add_argument('--include_disease', help='', required=False, type=bool)
    parser_identifier.add_argument('--min_entities', help='', required=False, type=str)
    parser_identifier.add_argument('--max_entities', help='', required=False, type=str)
    parser_identifier.add_argument('--projection', help='', required=False, type=bool)

    parser_identifier.set_defaults(func=analysis.identifier)

    parser_identifiers = subparsers.add_parser('identifiers', help='')
    parser_identifiers.add_argument('--ids', help='', required=False, type=str)
    parser_identifiers.add_argument('--interactors', help='', required=False, type=bool)
    parser_identifiers.add_argument('--page_size', help='', required=False, type=str)
    parser_identifiers.add_argument('--page', help='', required=False, type=str)
    parser_identifiers.add_argument('--species', help='', required=False, type=str)
    parser_identifiers.add_argument('--sort_by', help='', required=False, type=str)
    parser_identifiers.add_argument('--order', help='', required=False, type=str)
    parser_identifiers.add_argument('--resource', help='', required=False, type=str)
    parser_identifiers.add_argument('--p_value', help='', required=False, type=str)
    parser_identifiers.add_argument('--include_disease', help='', required=False, type=bool)
    parser_identifiers.add_argument('--min_entities', help='', required=False, type=str)
    parser_identifiers.add_argument('--max_entities', help='', required=False, type=str)
    parser_identifiers.add_argument('--projection', help='', required=False, type=bool)

    parser_identifiers.set_defaults(func=analysis.identifiers)

    parser_identifiers_form = subparsers.add_parser('identifiers_form', help='')
    parser_identifiers_form.add_argument('--path', help='', required=True, type=str)
    parser_identifiers_form.add_argument('--interactors', help='', required=False, type=bool)
    parser_identifiers_form.add_argument('--page_size', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--page', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--species', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--sort_by', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--order', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--resource', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--p_value', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--include_disease', help='', required=False, type=bool)
    parser_identifiers_form.add_argument('--min_entities', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--max_entities', help='', required=False, type=str)
    parser_identifiers_form.add_argument('--projection', help='', required=False, type=bool)

    parser_identifiers_form.set_defaults(func=analysis.identifiers_form)

    parser_identifiers_url = subparsers.add_parser('identifiers_url', help='')
    parser_identifiers_url.add_argument('--url', help='', required=True, type=str)
    parser_identifiers_url.add_argument('--interactors', help='', required=False, type=bool)
    parser_identifiers_url.add_argument('--page_size', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--page', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--species', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--sort_by', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--order', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--resource', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--p_value', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--include_disease', help='', required=False, type=bool)
    parser_identifiers_url.add_argument('--min_entities', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--max_entities', help='', required=False, type=str)
    parser_identifiers_url.add_argument('--projection', help='', required=False, type=bool)

    parser_identifiers_url.set_defaults(func=analysis.identifiers_url)

    parser_result2json = subparsers.add_parser('result2json', help='')
    parser_result2json.add_argument('--token', help='', required=True, type=str)
    parser_result2json.add_argument('--path', help='', required=False, type=str)
    parser_result2json.add_argument('--file', help='', required=False, type=str)
    parser_result2json.add_argument('--save', help='', required=False, type=bool)
    parser_result2json.add_argument('--gzip', help='', required=False, type=bool)
    parser_result2json.add_argument('--chunk_size', help='', required=False, type=int)

    parser_result2json.set_defaults(func=analysis.result2json)

    parser_pathway2df = subparsers.add_parser('result2json', help='')
    parser_pathway2df.add_argument('--token', help='', required=True, type=str)
    parser_pathway2df.add_argument('--path', help='', required=False, type=str)
    parser_pathway2df.add_argument('--resource', help='', required=False, type=str)
    parser_pathway2df.add_argument('--file', help='', required=False, type=str)
    parser_pathway2df.add_argument('--save', help='', required=False, type=bool)
    parser_pathway2df.add_argument('--chunk_size', help='', required=False, type=int)

    parser_pathway2df.set_defaults(func=analysis.pathway2df)

    parser_found_entities = subparsers.add_parser('found_entities', help='')
    parser_found_entities.add_argument('--token', help='', required=True, type=str)
    parser_found_entities.add_argument('--path', help='', required=False, type=str)
    parser_found_entities.add_argument('--resource', help='', required=False, type=str)
    parser_found_entities.add_argument('--file', help='', required=False, type=str)
    parser_found_entities.add_argument('--save', help='', required=False, type=bool)
    parser_found_entities.add_argument('--chunk_size', help='', required=False, type=int)

    parser_found_entities.set_defaults(func=analysis.found_entities)

    parser_unfound_entities = subparsers.add_parser('unfound_entities', help='')
    parser_unfound_entities.add_argument('--token', help='', required=True, type=str)
    parser_unfound_entities.add_argument('--path', help='', required=False, type=str)
    parser_unfound_entities.add_argument('--resource', help='', required=False, type=str)
    parser_unfound_entities.add_argument('--file', help='', required=False, type=str)
    parser_unfound_entities.add_argument('--save', help='', required=False, type=bool)
    parser_unfound_entities.add_argument('--chunk_size', help='', required=False, type=int)

    parser_unfound_entities.set_defaults(func=analysis.unfound_entities)

    parser_db_name = subparsers.add_parser('db_name', help='')
    parser_db_name.set_defaults(func=analysis.db_name)

    parser_db_version = subparsers.add_parser('db_version', help='')
    parser_db_version.set_defaults(func=analysis.db_version)

    parser_report = subparsers.add_parser('report', help='')
    parser_report.add_argument('--token', help='', required=True, type=str)
    parser_report.add_argument('--path', help='', required=True, type=str)
    parser_report.add_argument('--file', help='', required=False, type=str)
    parser_report.add_argument('--resource', help='', required=False, type=str)
    parser_report.add_argument('--diagram_profile', help='', required=False, type=str)
    parser_report.add_argument('--analysis_profile', help='', required=False, type=str)
    parser_report.add_argument('--fireworks_profile', help='', required=False, type=str)
    parser_report.add_argument('--species', help='', required=False, type=str)
    parser_report.add_argument('--chunk_size', help='', required=False, type=int)

    parser_report.set_defaults(func=analysis.report)

    parser_compare_species = subparsers.add_parser('compare_species', help='')
    parser_compare_species.add_argument('--species', help='', required=False, type=str)
    parser_compare_species.add_argument('--page_size', help='', required=False, type=str)
    parser_compare_species.add_argument('--page', help='', required=False, type=str)
    parser_compare_species.add_argument('--sort_by', help='', required=False, type=str)
    parser_compare_species.add_argument('--order', help='', required=False, type=str)
    parser_compare_species.add_argument('--resource', help='', required=False, type=str)
    parser_compare_species.add_argument('--p_value', help='', required=False, type=str)

    parser_compare_species.set_defaults(func=analysis.compare_species)

    parser_identifiers_mapping = subparsers.add_parser('identifiers_mapping', help='')
    parser_identifiers_mapping.add_argument('--ids', help='', required=True, type=str)
    parser_identifiers_mapping.add_argument('--interactors', help='', required=True, type=bool)
    parser_identifiers_mapping.add_argument('--projection', help='', required=True, type=bool)

    parser_identifiers_mapping.set_defaults(func=analysis.identifiers_mapping)

    parser_identifiers_mapping_form = subparsers.add_parser('identifiers_mapping_form', help='')
    parser_identifiers_mapping_form.add_argument('--path', help='', required=True, type=bool)
    parser_identifiers_mapping_form.add_argument('--interactors', help='', required=False, type=bool)
    parser_identifiers_mapping_form.add_argument('--projection', help='', required=False, type=bool)

    parser_identifiers_mapping_form.set_defaults(func=analysis.identifiers_mapping_form)

    parser_identifiers_mapping_url = subparsers.add_parser('identifiers_mapping_url', help='')
    parser_identifiers_mapping_url.add_argument('--external_url', help='', required=True, type=bool)
    parser_identifiers_mapping_url.add_argument('--interactors', help='', required=False, type=bool)
    parser_identifiers_mapping_url.add_argument('--projection', help='', required=False, type=bool)

    parser_identifiers_mapping_url.set_defaults(func=analysis.identifiers_mapping_url)

    parser_token = subparsers.add_parser('token', help='')
    parser_token.add_argument('--token', help='', required=True, type=str)
    parser_token.add_argument('--species', help='', required=False, type=str)
    parser_token.add_argument('--page_size', help='', required=False, type=str)
    parser_token.add_argument('--page', help='', required=False, type=str)
    parser_token.add_argument('--sort_by', help='', required=False, type=str)
    parser_token.add_argument('--order', help='', required=False, type=str)
    parser_token.add_argument('--resource', help='', required=False, type=str)
    parser_token.add_argument('--p_value', help='', required=False, type=str)
    parser_token.add_argument('--include_disease', help='', required=False, type=str)
    parser_token.add_argument('--min_entities', help='', required=False, type=bool)
    parser_token.add_argument('--max_entities', help='', required=False, type=bool)

    parser_token.set_defaults(func=analysis.token)

    parser_token_pathways_result = subparsers.add_parser('token_pathways_result', help='')
    parser_token_pathways_result.add_argument('--token', help='', required=True, type=str)
    parser_token_pathways_result.add_argument('--pathways', help='', required=True, type=str)
    parser_token_pathways_result.add_argument('--species', help='', required=False, type=str)
    parser_token_pathways_result.add_argument('--resource', help='', required=False, type=str)
    parser_token_pathways_result.add_argument('--p_value', help='', required=False, type=str)
    parser_token_pathways_result.add_argument('--include_disease', help='', required=False, type=bool)
    parser_token_pathways_result.add_argument('--min_entities', help='', required=False, type=str)
    parser_token_pathways_result.add_argument('--max_entities', help='', required=False, type=str)

    parser_token_pathways_result.set_defaults(func=analysis.token_pathways_result)

    parser_token_filter_species = subparsers.add_parser('token_filter_species', help='')
    parser_token_filter_species.add_argument('--token', help='', required=True, type=str)
    parser_token_filter_species.add_argument('--species', help='', required=False, type=str)
    parser_token_filter_species.add_argument('--sort_by', help='', required=False, type=str)
    parser_token_filter_species.add_argument('--order', help='', required=False, type=str)
    parser_token_filter_species.add_argument('--resource', help='', required=False, type=str)

    parser_token_filter_species.set_defaults(func=analysis.token_filter_species)

    parser_token_pathways_summary = subparsers.add_parser('token_pathways_summary', help='')
    parser_token_pathways_summary.add_argument('--token', help='', required=True, type=str)
    parser_token_pathways_summary.add_argument('--pathways', help='', required=True, type=str)
    parser_token_pathways_summary.add_argument('--resource', help='', required=False, type=str)

    parser_token_pathways_summary.set_defaults(func=analysis.token_pathways_summary)

    parser_token_pathway_summary = subparsers.add_parser('token_pathway_summary', help='')
    parser_token_pathway_summary.add_argument('--token', help='', required=True, type=str)
    parser_token_pathway_summary.add_argument('--pathway', help='', required=True, type=str)
    parser_token_pathway_summary.add_argument('--resource', help='', required=False, type=str)
    parser_token_pathway_summary.add_argument('--page', help='', required=False, type=str)
    parser_token_pathway_summary.add_argument('--by', help='', required=False, type=str)

    parser_token_pathway_summary.set_defaults(func=analysis.token_pathway_summary)

    parser_token_unfound_identifiers = subparsers.add_parser('token_unfound_identifiers', help='')
    parser_token_unfound_identifiers.add_argument('--token', help='', required=True, type=str)
    parser_token_unfound_identifiers.add_argument('--page_size', help='', required=True, type=str)
    parser_token_unfound_identifiers.add_argument('--page', help='', required=True, type=str)

    parser_token_unfound_identifiers.set_defaults(func=analysis.token_unfound_identifiers)

    parser_token_pathway_page = subparsers.add_parser('token_pathway_page', help='')
    parser_token_pathway_page.add_argument('--token', help='', required=True, type=str)
    parser_token_pathway_page.add_argument('--pathway', help='', required=True, type=str)
    parser_token_pathway_page.add_argument('--page_size', help='', required=False, type=str)
    parser_token_pathway_page.add_argument('--sort_by', help='', required=False, type=str)
    parser_token_pathway_page.add_argument('--order', help='', required=False, type=str)
    parser_token_pathway_page.add_argument('--resource', help='', required=False, type=str)
    parser_token_pathway_page.add_argument('--p_value', help='', required=False, type=str)
    parser_token_pathway_page.add_argument('--include_disease', help='', required=False, type=bool)
    parser_token_pathway_page.add_argument('--min_entities', help='', required=False, type=str)
    parser_token_pathway_page.add_argument('--max_entities', help='', required=False, type=str)

    parser_token_pathway_page.set_defaults(func=analysis.token_pathway_page)

    parser_token_pathways_binned = subparsers.add_parser('token_pathways_binned', help='')
    parser_token_pathways_binned.add_argument('--token', help='', required=True, type=str)
    parser_token_pathways_binned.add_argument('--resource', help='', required=False, type=str)
    parser_token_pathways_binned.add_argument('--bin_size', help='', required=False, type=str)
    parser_token_pathways_binned.add_argument('--p_value', help='', required=False, type=str)
    parser_token_pathways_binned.add_argument('--include_disease', help='', required=False, type=bool)

    parser_token_pathways_binned.set_defaults(func=analysis.token_pathways_binned)

    parser_token_pathways_reactions = subparsers.add_parser('token_pathways_reactions', help='')
    parser_token_pathways_reactions.add_argument('--token', help='', required=True, type=str)
    parser_token_pathways_reactions.add_argument('--pathways', help='', required=True, type=str)
    parser_token_pathways_reactions.add_argument('--resource', help='', required=False, type=str)
    parser_token_pathways_reactions.add_argument('--p_value', help='', required=False, type=str)
    parser_token_pathways_reactions.add_argument('--include_disease', help='', required=False, type=bool)
    parser_token_pathways_reactions.add_argument('--min_entities', help='', required=False, type=str)
    parser_token_pathways_reactions.add_argument('--max_entities', help='', required=False, type=str)

    parser_token_pathways_reactions.set_defaults(func=analysis.token_pathways_reactions)

    parser_token_pathway_reactions = subparsers.add_parser('token_pathway_reactions', help='')
    parser_token_pathway_reactions.add_argument('--token', help='', required=True, type=str)
    parser_token_pathway_reactions.add_argument('--pathway', help='', required=True, type=str)
    parser_token_pathway_reactions.add_argument('--resource', help='', required=False, type=str)
    parser_token_pathway_reactions.add_argument('--p_value', help='', required=False, type=str)
    parser_token_pathway_reactions.add_argument('--include_disease', help='', required=False, type=bool)
    parser_token_pathway_reactions.add_argument('--min_entities', help='', required=False, type=str)
    parser_token_pathway_reactions.add_argument('--max_entities', help='', required=False, type=str)

    parser_token_pathway_reactions.set_defaults(func=analysis.token_pathway_reactions)

    parser_token_resources = subparsers.add_parser('token_resources', help='')
    parser_token_resources.add_argument('--token', help='', required=True, type=str)

    parser_token_resources.set_defaults(func=analysis.token_resources)

    parser_import_json = subparsers.add_parser('import_json', help='')
    parser_import_json.add_argument('--input_json', help='', required=True, type=object)

    parser_import_json.set_defaults(func=analysis.import_json)

    parser_import_form = subparsers.add_parser('import_form', help='')
    parser_import_form.add_argument('--input_file', help='', required=True, type=str)

    parser_import_form.set_defaults(func=analysis.import_form)

    parser_import_url = subparsers.add_parser('import_url', help='')
    parser_import_url.add_argument('--input_url', help='', required=True, type=str)

    parser_import_url.set_defaults(func=analysis.import_url)

    # content service --------------------------------------------------
    parser_discover = subparsers.add_parser('discover', help='')
    parser_discover.add_argument('--id', help='', required=True)

    parser_discover.set_defaults(func=content.discover)

    parser_disease = subparsers.add_parser('disease', help='')
    parser_disease.add_argument('--doid', help='', required=False, type=bool)

    parser_disease.set_defaults(func=content.disease)

    parser_entities_complex = subparsers.add_parser('entities_complex', help='')
    parser_entities_complex.add_argument('--id', help='', required=False, type=str)

    parser_entities_complex.set_defaults(func=content.entities_complex)

    parser_entities_complexes = subparsers.add_parser('entities_complexes', help='')
    parser_entities_complexes.add_argument('--id', help='', required=False, type=str)
    parser_entities_complexes.add_argument('--resource', help='', required=False, type=str)

    parser_entities_complexes.set_defaults(func=content.entities_complexes)

    parser_entity_structures = subparsers.add_parser('entity_structures', help='')
    parser_entity_structures.add_argument('--id', help='', required=False, type=str)

    parser_entity_structures.set_defaults(func=content.entity_structures)

    parser_entity_other_form = subparsers.add_parser('entity_other_form', help='')
    parser_entity_other_form.add_argument('--id', help='', required=False, type=str)

    parser_entity_other_form.set_defaults(func=content.entity_other_form)

    parser_event_ancestors = subparsers.add_parser('event_ancestors', help='')
    parser_event_ancestors.add_argument('--id', help='', required=False, type=str)

    parser_event_ancestors.set_defaults(func=content.event_ancestors)

    parser_event_species = subparsers.add_parser('event_species', help='')
    parser_event_species.add_argument('--species', help='', required=False, type=str)

    parser_event_species.set_defaults(func=content.event_species)

    parser_export_diagram = subparsers.add_parser('export_diagram', help='')
    parser_export_diagram.add_argument('--id', help='', required=False, type=str)
    parser_export_diagram.add_argument('--ext', help='', required=False, type=str)
    parser_export_diagram.add_argument('--quality', help='', required=False, type=str)
    parser_export_diagram.add_argument('--flag_interactors', help='', required=False, type=bool)
    parser_export_diagram.add_argument('--title', help='', required=False, type=bool)
    parser_export_diagram.add_argument('--margin', help='', required=False, type=str)
    parser_export_diagram.add_argument('--ehld', help='', required=False, type=bool)
    parser_export_diagram.add_argument('--diagram_profile', help='', required=False, type=str)
    parser_export_diagram.add_argument('--resource', help='', required=False, type=str)
    parser_export_diagram.add_argument('--analysis_profile', help='', required=False, type=str)
    parser_export_diagram.add_argument('--token', help='', required=False, type=str)
    parser_export_diagram.add_argument('--flag', help='', required=False, type=str)
    parser_export_diagram.add_argument('--sel', nargs='+', help='', required=False)
    parser_export_diagram.add_argument('--exp_column', help='', required=False, type=str)
    parser_export_diagram.add_argument('--file', help='', required=False, type=str)
    parser_export_diagram.add_argument('--path', help='', required=False, type=str)

    parser_export_diagram.set_defaults(func=content.export_diagram)

    parser_export_document = subparsers.add_parser('export_document', help='')
    parser_export_document.add_argument('--id', help='', required=False, type=str)
    parser_export_document.add_argument('--level', help='', required=False, type=str)
    parser_export_document.add_argument('--diagram_profile', help='', required=False, type=str)
    parser_export_document.add_argument('--resource', help='', required=False, type=str)
    parser_export_document.add_argument('--analysis_profile', help='', required=False, type=str)
    parser_export_document.add_argument('--token', help='', required=False, type=str)
    parser_export_document.add_argument('--exp_column', help='', required=False, type=str)
    parser_export_document.add_argument('--file', help='', required=False, type=str)
    parser_export_document.add_argument('--path', help='', required=False, type=str)

    parser_export_document.set_defaults(func=content.export_document)

    parser_export_event = subparsers.add_parser('export_event', help='')
    parser_export_event.add_argument('--id', help='', required=False, type=str)
    parser_export_event.add_argument('--format', help='', required=False, type=str)
    parser_export_event.add_argument('--file', help='', required=False, type=str)
    parser_export_event.add_argument('--path', help='', required=False, type=str)

    parser_export_event.set_defaults(func=content.export_event)

    parser_export_fireworks = subparsers.add_parser('export_fireworks', help='')
    parser_export_fireworks.add_argument('--species', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--ext', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--file', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--path', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--quality', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--flag', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--flag_interactors', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--sel', help='', nargs='+', required=False)
    parser_export_fireworks.add_argument('--title', help='', required=False, type=bool)
    parser_export_fireworks.add_argument('--margin', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--resource', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--diagram_profile', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--coverage', help='', required=False, type=bool)
    parser_export_fireworks.add_argument('--token', help='', required=False, type=str)
    parser_export_fireworks.add_argument('--exp_column', help='', required=False, type=str)

    parser_export_fireworks.set_defaults(func=content.export_fireworks)

    parser_export_reaction = subparsers.add_parser('export_reaction', help='')
    parser_export_reaction.add_argument('--id', help='', required=False, type=str)
    parser_export_reaction.add_argument('--ext', help='', required=False, type=str)
    parser_export_reaction.add_argument('--quality', help='', required=False, type=str)
    parser_export_reaction.add_argument('--flag_interactors', help='', required=False, type=bool)
    parser_export_reaction.add_argument('--coverage', help='', required=False, type=bool)
    parser_export_reaction.add_argument('--title', help='', required=False, type=bool)
    parser_export_reaction.add_argument('--margin', help='', required=False, type=str)
    parser_export_reaction.add_argument('--diagram_profile', help='', required=False, type=str)
    parser_export_reaction.add_argument('--resource', help='', required=False, type=str)
    parser_export_reaction.add_argument('--token', help='', required=False, type=str)
    parser_export_reaction.add_argument('--flag', help='', required=False, type=str)
    parser_export_reaction.add_argument('--sel', nargs='+', help='', required=False)
    parser_export_reaction.add_argument('--exp_column', help='', required=False, type=str)
    parser_export_reaction.add_argument('--file', help='', required=False, type=str)
    parser_export_reaction.add_argument('--path', help='', required=False, type=str)

    parser_export_reaction.set_defaults(func=content.export_reaction)

    parser_interactors_psicquic_acc = subparsers.add_parser('interactors_psicquic_acc', help='')
    parser_interactors_psicquic_acc.add_argument('--acc', help='', required=False, type=str)
    parser_interactors_psicquic_acc.add_argument('--resource', help='', required=False, type=str)
    parser_interactors_psicquic_acc.add_argument('--by', help='', required=False, type=str)

    parser_interactors_psicquic_acc.set_defaults(func=content.interactors_psicquic_acc)

    parser_interactors_psicquic_accs = subparsers.add_parser('interactors_psicquic_accs', help='')
    parser_interactors_psicquic_accs.add_argument('--proteins', help='', required=False, type=str)
    parser_interactors_psicquic_accs.add_argument('--resource', help='', required=False, type=str)
    parser_interactors_psicquic_accs.add_argument('--by', help='', required=False, type=str)

    parser_interactors_psicquic_accs.set_defaults(func=content.interactors_psicquic_accs)

    parser_interactors_psicquic_resources = subparsers.add_parser('interactors_psicquic_resources', help='')
    parser_interactors_psicquic_resources.set_defaults(func=content.interactors_psicquic_resources)

    parser_interactors_static_acc = subparsers.add_parser('interactors_static_acc', help='')
    parser_interactors_static_acc.add_argument('--acc', help='', required=False, type=str)
    parser_interactors_static_acc.add_argument('--page', help='', required=False, type=str)
    parser_interactors_static_acc.add_argument('--page_size', help='', required=False, type=str)
    parser_interactors_static_acc.add_argument('--by', help='', required=False, type=str)

    parser_interactors_static_acc.set_defaults(func=content.interactors_static_acc)

    parser_interactors_acc_pathways = subparsers.add_parser('interactors_acc_pathways', help='')
    parser_interactors_acc_pathways.add_argument('--acc', help='', required=False, type=str)
    parser_interactors_acc_pathways.add_argument('--species', help='', required=False, type=str)
    parser_interactors_acc_pathways.add_argument('--only_diagrammed', help='', required=False, type=bool)

    parser_interactors_acc_pathways.set_defaults(func=content.interactors_acc_pathways)

    parser_interactors_static_accs = subparsers.add_parser('interactors_static_accs', help='')
    parser_interactors_static_accs.add_argument('--accs', help='', required=False, type=str)
    parser_interactors_static_accs.add_argument('--by', help='', required=False, type=str)
    parser_interactors_static_accs.add_argument('--page', help='', required=False, type=str)
    parser_interactors_static_accs.add_argument('--page_size', help='', required=False, type=str)

    parser_interactors_static_accs.set_defaults(func=content.interactors_static_accs)

    parser_token_interactors = subparsers.add_parser('token_interactors', help='')
    parser_token_interactors.add_argument('--token', help='', required=True, type=str)
    parser_token_interactors.add_argument('--proteins', help='', required=True, type=str)

    parser_token_interactors.set_defaults(func=content.token_interactors)

    parser_interactors_psicquic_url = subparsers.add_parser('interactors_psicquic_url', help='')
    parser_interactors_psicquic_url.add_argument('--name', help='', required=True, type=str)
    parser_interactors_psicquic_url.add_argument('--psicquic_url', help='', required=True, type=str)

    parser_interactors_psicquic_url.set_defaults(func=content.interactors_psicquic_url)

    parser_interactors_upload_content = subparsers.add_parser('interactors_upload_content', help='')
    parser_interactors_upload_content.add_argument('--name', help='', required=True, type=str)
    parser_interactors_upload_content.add_argument('--content', help='', required=True, type=str)

    parser_interactors_upload_content.set_defaults(func=content.interactors_upload_content)

    parser_interactors_form = subparsers.add_parser('interactors_form', help='')
    parser_interactors_form.add_argument('--path', help='', required=True, type=str)
    parser_interactors_form.add_argument('--name', help='', required=True, type=str)

    parser_interactors_form.set_defaults(func=content.interactors_form)

    parser_interactors_url = subparsers.add_parser('interactors_url', help='')
    parser_interactors_url.add_argument('--name', help='', required=True, type=str)
    parser_interactors_url.add_argument('--interactors_url', help='', required=True, type=str)

    parser_interactors_url.set_defaults(func=content.interactors_url)

    parser_mapping = subparsers.add_parser('mapping', help='')
    parser_mapping.add_argument('--id', help='', required=False, type=str)
    parser_mapping.add_argument('--resource', help='', required=False, type=str)
    parser_mapping.add_argument('--species', help='', required=False, type=str)
    parser_mapping.add_argument('--by', help='', required=False, type=str)

    parser_mapping.set_defaults(func=content.mapping)

    parser_orthology_events = subparsers.add_parser('orthology_events', help='')
    parser_orthology_events.add_argument('--ids', help='', required=True, type=str)
    parser_orthology_events.add_argument('--species', help='', required=True, type=str)

    parser_orthology_events.set_defaults(func=content.orthology_events)

    parser_orthology = subparsers.add_parser('orthology', help='')
    parser_orthology.add_argument('--id', help='', required=False, type=str)
    parser_orthology.add_argument('--species', help='', required=False, type=str)

    parser_orthology.set_defaults(func=content.orthology)

    parser_participants = subparsers.add_parser('participants', help='')
    parser_participants.add_argument('--id', help='', required=False, type=str)

    parser_participants.set_defaults(func=content.participants)

    parser_participants_physical_entities = subparsers.add_parser('participants_physical_entities', help='')
    parser_participants_physical_entities.add_argument('--id', help='', required=False, type=str)

    parser_participants_physical_entities.set_defaults(func=content.participants_physical_entities)

    parser_participants_reference_entities = subparsers.add_parser('participants_reference_entities', help='')
    parser_participants_reference_entities.add_argument('--id', help='', required=False, type=str)

    parser_participants_reference_entities.set_defaults(func=content.participants_reference_entities)

    parser_pathway_contained_event = subparsers.add_parser('pathway_contained_event', help='')
    parser_pathway_contained_event.add_argument('--id', help='', required=False, type=str)

    parser_pathway_contained_event.set_defaults(func=content.pathway_contained_event)

    parser_pathway_contained_event_atttibute = subparsers.add_parser('pathway_contained_event_atttibute', help='')
    parser_pathway_contained_event_atttibute.add_argument('--id', help='', required=False, type=str)
    parser_pathway_contained_event_atttibute.add_argument('--attribute', help='', required=False, type=str)

    parser_pathway_contained_event_atttibute.set_defaults(func=content.pathway_contained_event_atttibute)

    parser_pathways_low_diagram = subparsers.add_parser('pathways_low_diagram', help='')
    parser_pathways_low_diagram.add_argument('--id', help='', required=False, type=str)
    parser_pathways_low_diagram.add_argument('--species', help='', required=False, type=str)
    parser_pathways_low_diagram.add_argument('--all_forms', help='', required=False, type=bool)

    parser_pathways_low_diagram.set_defaults(func=content.pathways_low_diagram)

    parser_pathways_low_entity = subparsers.add_parser('pathways_low_entity', help='')
    parser_pathways_low_entity.add_argument('--id', help='', required=False, type=str)
    parser_pathways_low_entity.add_argument('--species', help='', required=False, type=str)
    parser_pathways_low_entity.add_argument('--all_forms', help='', required=False, type=bool)

    parser_pathways_low_entity.set_defaults(func=content.pathways_low_entity)

    parser_pathways_top_level = subparsers.add_parser('pathways_top_level', help='')
    parser_pathways_top_level.add_argument('--species', help='', required=False, type=str)

    parser_pathways_top_level.set_defaults(func=content.pathways_top_level)

    parser_person_name = subparsers.add_parser('person_name', help='')
    parser_person_name.add_argument('--name', help='', required=False, type=str)
    parser_person_name.add_argument('--exact', help='', required=False, type=bool)

    parser_person_name.set_defaults(func=content.person_name)

    parser_person_id = subparsers.add_parser('person_id', help='')
    parser_person_id.add_argument('--id', help='', required=False, type=str)
    parser_person_id.add_argument('--by', help='', required=False, type=str)
    parser_person_id.add_argument('--attribute', help='', required=False, type=str)

    parser_person_id.set_defaults(func=content.person_id)

    parser_query_id = subparsers.add_parser('query_id', help='')
    parser_query_id.add_argument('--id', help='', required=False, type=str)
    parser_query_id.add_argument('--enhanced', help='', required=False, type=bool)
    parser_query_id.add_argument('--attribute', help='', required=False, type=str)

    parser_query_id.set_defaults(func=content.query_id)

    parser_query_ids = subparsers.add_parser('query_ids', help='')
    parser_query_ids.add_argument('--ids', help='', required=False, type=str)
    parser_query_ids.add_argument('--mapping', help='', required=False, type=bool)

    parser_query_ids.set_defaults(func=content.query_ids)

    parser_references = subparsers.add_parser('references', help='')
    parser_references.add_argument('--id', help='', required=False, type=str)

    parser_references.set_defaults(func=content.references)

    parser_species = subparsers.add_parser('species', help='')
    parser_species.add_argument('--by', help='', required=False, type=str)

    parser_species.set_defaults(func=content.species)

    parser_schema = subparsers.add_parser('schema', help='')
    parser_schema.add_argument('--name', help='', required=False, type=str)
    parser_schema.add_argument('--by', help='', required=False, type=str)
    parser_schema.add_argument('--species', help='', required=False, type=str)
    parser_schema.add_argument('--page', help='', required=False, type=str)
    parser_schema.add_argument('--offset', help='', required=False, type=str)

    parser_schema.set_defaults(func=content.schema)

    parser_search_diagram = subparsers.add_parser('search_diagram', help='')
    parser_search_diagram.add_argument('--diagram', help='', required=False, type=str)
    parser_search_diagram.add_argument('--query', help='', required=False, type=str)
    parser_search_diagram.add_argument('--types', nargs='+',  help='', required=False)
    parser_search_diagram.add_argument('--start', help='', required=False, type=str)
    parser_search_diagram.add_argument('--rows', help='', required=False, type=str)

    parser_search_diagram.set_defaults(func=content.search_diagram)

    parser_search_diagram_instance = subparsers.add_parser('search_diagram_instance', help='')
    parser_search_diagram_instance.add_argument('--diagram', help='', required=False, type=str)
    parser_search_diagram_instance.add_argument('--instance', help='', required=False, type=str)
    parser_search_diagram_instance.add_argument('--types', nargs='+',  help='', required=False)

    parser_search_diagram_instance.set_defaults(func=content.search_diagram_instance)

    parser_search_diagram_pathway_flag = subparsers.add_parser('search_diagram_pathway_flag', help='')
    parser_search_diagram_pathway_flag.add_argument('--diagram', help='', required=False, type=str)
    parser_search_diagram_pathway_flag.add_argument('--query', help='', required=False, type=str)

    parser_search_diagram_pathway_flag.set_defaults(func=content.search_diagram_pathway_flag)

    parser_search_facet = subparsers.add_parser('search_facet', help='')
    parser_search_facet.set_defaults(func=content.search_facet)

    parser_search_facet_query = subparsers.add_parser('search_facet_query', help='')
    parser_search_facet_query.add_argument('--query', help='', required=False, type=str)
    parser_search_facet_query.add_argument('--species', help='', nargs='+', required=False)
    parser_search_facet_query.add_argument('--types', help='', nargs='+', required=False)
    parser_search_facet_query.add_argument('--compartments', help='', nargs='+', required=False)
    parser_search_facet_query.add_argument('--keywords', help='', nargs='+', required=False)

    parser_search_facet_query.set_defaults(func=content.search_facet_query)

    parser_search_fireworks = subparsers.add_parser('search_fireworks', help='')
    parser_search_fireworks.add_argument('--query', help='', required=False, type=str)
    parser_search_fireworks.add_argument('--species', help='', required=False, type=str)
    parser_search_fireworks.add_argument('--types', help='', nargs='+', required=False)
    parser_search_fireworks.add_argument('--start', help='', required=False, type=str)
    parser_search_fireworks.add_argument('--rows', help='', required=False, type=str)

    parser_search_fireworks.set_defaults(func=content.search_fireworks)

    parser_search_fireworks_flag = subparsers.add_parser('search_fireworks_flag', help='')
    parser_search_fireworks_flag.add_argument('--query', help='', required=False, type=str)
    parser_search_fireworks_flag.add_argument('--species', help='', required=False, type=str)

    parser_search_fireworks_flag.set_defaults(func=content.search_fireworks_flag)

    parser_search_query = subparsers.add_parser('search_query', help='')
    parser_search_query.add_argument('--query', help='', required=False, type=str)
    parser_search_query.add_argument('--species', help='', nargs='+', required=False)
    parser_search_query.add_argument('--types', help='', nargs='+', required=False)
    parser_search_query.add_argument('--compartments', help='', nargs='+', required=False)
    parser_search_query.add_argument('--keywords', help='', nargs='+', required=False)
    parser_search_query.add_argument('--cluster', help='', required=False, type=bool)
    parser_search_query.add_argument('--start', help='', required=False, type=str)
    parser_search_query.add_argument('--rows', help='', required=False, type=str)

    parser_search_query.set_defaults(func=content.search_query)

    parser_search_spellcheck = subparsers.add_parser('search_spellcheck', help='')
    parser_search_spellcheck.add_argument('--query', help='', required=False, type=str)

    parser_search_spellcheck.set_defaults(func=content.search_spellcheck)

    parser_search_suggest = subparsers.add_parser('search_suggest', help='')
    parser_search_suggest.add_argument('--query', help='', required=False, type=str)

    parser_search_suggest.set_defaults(func=content.search_suggest)

    parser_testing = subparsers.add_parser('testing', help='')
    parser_testing.set_defaults(func=testing)

    return parser


def perform_main(args):
    if 'func' in args:
        try:
            args.func(args)
        except Exception as ex:
            print(ex)


def main():
    args = build_parser().parse_args()
    perform_main(args)


if __name__ == "__main__":
    main()
