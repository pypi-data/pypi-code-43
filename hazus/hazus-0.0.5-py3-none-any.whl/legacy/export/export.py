# from .reports import *
# from .results import *
# from . import reports
# from . import results
from .Setup_Connection import setup
from importlib import import_module

def export(inputs):
    """
    Report tabular, spatial, and report data from Hazus legacy
     
    Keyword arguments: \n
        inputs: dictionary = {
            'opt_csv': boolean,
            'opt_shp': boolean,
            'opt_report': boolean,
            'opt_json': boolean,
            'study_region': str -- your study region name,
            'title': str -- title for the report,
            'meta': str -- sub-title for the report,
        }
    """
    comp_name, cnxn, date, modules = setup(inputs)
    inputs.update({'created': date})
    result_module = import_module('.'+modules['result_module'], package='hazus.legacy.export.results')
    report_module = import_module('.'+modules['report_module'], package='hazus.legacy.export.reports')
    hazus_results_dict, subcounty_results, county_results, damaged_essential_facilities = result_module.read_sql(comp_name, cnxn, inputs)
    if inputs['opt_csv']:
        result_module.to_csv(hazus_results_dict, subcounty_results, county_results, damaged_essential_facilities, inputs)
    if inputs['opt_report']:
        gdf = result_module.to_shp(inputs, hazus_results_dict, subcounty_results)
        report_module.generate_report(gdf, hazus_results_dict, subcounty_results, county_results, inputs)