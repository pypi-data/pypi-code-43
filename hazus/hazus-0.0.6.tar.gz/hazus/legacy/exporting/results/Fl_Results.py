import pandas as pd
from shapely.wkt import loads
from shapely.geometry import mapping, Polygon
import fiona
import geopandas as gpd
import numpy as np
from time import time
import sys
import json


def read_sql(comp_name, cnxn, inputs):
    # removes all infinite and nulls values
    def setValuesValid(df):
        if type(df) == pd.DataFrame:
            cols = df.columns
            for col in cols:
                try:
                    dtypes = df[col].apply(type).unique()
                    if (col != 'geometry') & (str not in dtypes):
                        # sets null values to 0
                        df[col][df[col].isnull()] = 0
                        if (np.bool in dtypes) or (np.bool_ in dtypes):
                            df[col] = df[col].astype(int)
                        # ensure values are finite
                        df.replace([np.inf, -np.inf], 0)
                except:
                    print('ERR ------- ' + col)
        return df
        
    #Select results from SQL Server Hazus study region database
    # sql_econ_loss = """SELECT CensusBlock, SUM(ISNULL(TotalLoss, 0))
    # AS TotalLoss, SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
    # SUM(ISNULL(ContentsLoss, 0)) AS ContLoss FROM %s.dbo.[flFRGBSEcLossByTotal]
    # Group by CensusBlock""" %inputs['study_region']

    sql_econ_loss ="""
        IF EXISTS 
            (SELECT TOP (1) ReturnPeriodId 
            FROM {s}.dbo.[flFRGBSEcLossByTotal] 
            WHERE ReturnPeriodId = '100')
                BEGIN
                    SELECT 
                        CensusBlock,
                        SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
                        SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
                        SUM(ISNULL(ContentsLoss, 0)) AS ContLoss 
                            FROM {s}.dbo.[flFRGBSEcLossByTotal]
                            WHERE ReturnPeriodId = '100'
                            Group by CensusBlock
                END
        ELSE IF EXISTS 
            (SELECT TOP (1) ReturnPeriodId 
            FROM {s}.dbo.[flFRGBSEcLossByTotal] 
            WHERE ReturnPeriodId = '500')
                BEGIN
                    SELECT 
                        CensusBlock,
                        SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
                        SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
                        SUM(ISNULL(ContentsLoss, 0)) AS ContLoss 
                            FROM {s}.dbo.[flFRGBSEcLossByTotal]
                            WHERE ReturnPeriodId = '500'
                            Group by CensusBlock
                END
        ELSE IF EXISTS 
            (SELECT TOP (1) ReturnPeriodId 
            FROM {s}.dbo.[flFRGBSEcLossByTotal] 
            WHERE ReturnPeriodId = '50')
                BEGIN
                    SELECT 
                        CensusBlock,
                        SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
                        SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
                        SUM(ISNULL(ContentsLoss, 0)) AS ContLoss 
                            FROM {s}.dbo.[flFRGBSEcLossByTotal]
                            WHERE ReturnPeriodId = '50'
                            Group by CensusBlock
                END
        ELSE IF EXISTS 
            (SELECT TOP (1) ReturnPeriodId 
            FROM {s}.dbo.[flFRGBSEcLossByTotal] 
            WHERE ReturnPeriodId = '25')
                BEGIN
                    SELECT 
                        CensusBlock,
                        SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
                        SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
                        SUM(ISNULL(ContentsLoss, 0)) AS ContLoss 
                            FROM {s}.dbo.[flFRGBSEcLossByTotal]
                            WHERE ReturnPeriodId = '25'
                            Group by CensusBlock
                END
        ELSE IF EXISTS 
            (SELECT TOP (1) ReturnPeriodId 
            FROM {s}.dbo.[flFRGBSEcLossByTotal] 
            WHERE ReturnPeriodId = '10')
                BEGIN
                    SELECT 
                        CensusBlock,
                        SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
                        SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
                        SUM(ISNULL(ContentsLoss, 0)) AS ContLoss 
                            FROM {s}.dbo.[flFRGBSEcLossByTotal]
                            WHERE ReturnPeriodId = '10'
                            Group by CensusBlock
                END
        ELSE
            BEGIN
                SELECT 
                CensusBlock,
                SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
                SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
                SUM(ISNULL(ContentsLoss, 0)) AS ContLoss 
                FROM {s}.dbo.[flFRGBSEcLossByTotal]
                Group by CensusBlock
            END
    """.format(s=inputs['study_region'])

    sql_demographics = """SELECT CensusBlock, Population, Households FROM
    %s.dbo.[hzDemographicsB]""" %inputs['study_region']

    sql_impact = """SELECT {s}.dbo.flFRDebris.CensusBlock, TotalTons AS Debris,
    DisplacedPop AS DisplPop, ShortTermNeeds AS Shelter
    FROM {s}.dbo.[flFRDebris] LEFT JOIN {s}.dbo.flFRShelter ON
    {s}.dbo.flFRDebris.CensusBlock = {s}.dbo.flFRShelter.CensusBlock""".format(s=inputs['study_region'])

    # TODO correct integer error so that building damage counts are accurate
    
    #sql_building_damage = """SELECT CensusBlock, SUM(ISNULL(TotalBldgCount, 0)) AS TotalBldgs,
    #SUM(ISNULL(CountNoDmg, 0)) AS NoDamage, SUM(ISNULL(CountSubstantialDmg, 0)) AS Extensive
    #FROM %s.dbo.[flFRGBSDmgCountGBldgType] GROUP BY CensusBlock""" %inputs['study_region']

    
    #sql_building_damage_occup = """SELECT GenOccup AS Occupancy, SUM(ISNULL(TotalBldgCount, 0))
    #AS TotalBldgs, SUM(ISNULL([CountDmg1to10], 0) AS Affected,
    #SUM(ISNULL([CountDmg11to20], 0) AS Minor,
    #SUM(ISNULL(([CountDmg21to30] + [CountDmg31to40] + [CountDmg41to50]), 0)) AS Major,
    #SUM(ISNULL(([CountDmg51to60] + [CountDmg61to70] + [CountDmg71to80], + 
    #[CountDmg81to90], + [CountDmg91to100]), 0)) AS Substantial
    #FROM %s.dbo.[flFRGBSDmgCountGOccupB] GROUP BY GenOccup""" %inputs['study_region']

    #sql_building_damage_bldg_type = """SELECT BldgType, SUM(ISNULL(TotalBldgCount, 0)) AS TotalBldgs,
    #SUM(ISNULL(CountNoDmg, 0)) AS NoDamage, SUM(ISNULL(CountSubstantialDmg, 0)) AS Extensive
    #FROM %s.dbo.[flFRGBSDmgCountGBldgType] GROUP BY BldgType""" %inputs['study_region']
    
    sql_econ_loss_occup = """SELECT SOccup AS Occupancy, SUM(ISNULL(TotalLoss, 0))
    AS TotalLoss, SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss,
    SUM(ISNULL(ContentsLoss, 0)) AS ContLoss
    FROM %s.dbo.[flFRGBSEcLossBySOccup] GROUP BY SOccup""" %inputs['study_region']

    sql_econ_loss_bldg_type = """SELECT BldgType, SUM(ISNULL(TotalLoss, 0)) AS TotalLoss,
    SUM(ISNULL(BuildingLoss, 0)) AS BldgLoss, SUM(ISNULL(ContentsLoss, 0)) AS ContLoss
    FROM %s.dbo.[flFRGBSEcLossByGBldgType] GROUP BY BldgType""" %inputs['study_region']

    sql_spatial = """SELECT CensusBlock, Tract, Shape.STAsText() AS Shape
    FROM %s.dbo.[hzCensusBlock_TIGER]""" %inputs['study_region']

    sql_county_fips = """SELECT Tract, {s}.dbo.hzCounty.CountyFips, {s}.dbo.hzCounty.CountyName, {s}.dbo.hzCounty.State
    FROM {s}.dbo.[hzTract] FULL JOIN {s}.dbo.hzCounty ON {s}.dbo.hzTract.CountyFips
    = {s}.dbo.hzCounty.CountyFips""".format(s=inputs['study_region'])

    sql_scenarios = """SELECT [StudyCaseName] FROM %s.[dbo].[flStudyCase]""" %inputs['study_region']

    #Group tables and queries into iterable
    hazus_results = {'econ_loss': sql_econ_loss,'demographics': sql_demographics,
                    'impact': sql_impact,'econ_loss_occup': sql_econ_loss_occup,
                    'econ_loss_bldg_type': sql_econ_loss_bldg_type,
                    'censusblock_spatial': sql_spatial,
                    'county_fips': sql_county_fips,
                    'scenarios': sql_scenarios}

    #Read result tables from SQL Server into dataframes with Census ID as index
    try:
        hazus_results_dict = {table: pd.read_sql(query, cnxn) for table, query
        in hazus_results.iteritems()}
        for name, dataframe in hazus_results_dict.iteritems():
            if (name != 'econ_loss_occup') and (name != 'econ_loss_bldg_type'):
                try: 
                    dataframe.set_index('CensusBlock', append=False, inplace=True)
                except:
                    pass
    except:
        hazus_results_dict = {table: pd.read_sql(query, cnxn) for table, query
        in hazus_results.items()}
        for name, dataframe in hazus_results_dict.items():
            if (name != 'econ_loss_occup') and (name != 'econ_loss_bldg_type'):
                try: 
                    dataframe.set_index('CensusBlock', append=False, inplace=True)
                except:
                    pass

    # Convert units to real $$ bills y'all
    hazus_results_dict['econ_loss'] = hazus_results_dict['econ_loss'] * 1000
    # Convert units to tons
    debris_cols = ['Debris']
    for debris_col in debris_cols:
        hazus_results_dict['impact'][debris_col] = hazus_results_dict['impact'][debris_col] * 1000

    def prepBuildingDamageOccup(econ_loss_occup):
        hrd_elo = econ_loss_occup
        # summarize building damage by occupancy type
        oc_dict = {
            'RES': 'Residential',
            'COM': 'Commercial',
            'IND': 'Industry',
            'AGR': 'Agriculture',
            'EDU': 'Education',
            'REL': 'Religious',
            'GOV': 'Government'
        }
        hrd_elo['Occupancy'] = hrd_elo['Occupancy'].apply(lambda x: x.strip())
        for key in oc_dict:
            hrd_elo['Occupancy'][hrd_elo['Occupancy'].str.contains(key)] = oc_dict[key]
        replacements = {
            'BldgLoss': 'Building',
            'ContLoss': 'Content',
            'TotalLoss': 'Total'
        }
        for replace in replacements.items():
            hrd_elo.columns = [x.replace(replace[0], replace[1]) if x == replace[0] else x for x in hrd_elo.columns]
        return hrd_elo

    def prepEconLossByType(econ_loss_bldg_type):
        hrd_elbt = econ_loss_bldg_type
        # hrd_elbt = hazus_results_dict['econ_loss_bldg_type']
        hrd_elbt['BldgType'][hrd_elbt['BldgType'] == 'ManufHousing'] = 'Manufactured'
        replacements = {
            'BldgType': 'Type',
            'BldgLoss': 'Building',
            'ContLoss': 'Content',
            'TotalLoss': 'Total'
        }
        for replace in replacements.items():
            hrd_elbt.columns = [x.replace(replace[0], replace[1]) if x == replace[0] else x for x in hrd_elbt.columns]
        return hrd_elbt


    def prepBarPlot(df, summarize_field, hues):
        summarized = df.groupby(summarize_field).sum()
        summarized = summarized.reset_index()
        new_df = pd.DataFrame()
        for hue in hues:
            hue_df = summarized[[summarize_field, hue]]
            hue_df.columns = ['Type', 'Total']
            hue_df['Status'] = hue
            new_df = new_df.append(hue_df)
        new_df['Total'] = (new_df['Total'] + 0.5).apply(int)
        return new_df
    
    #Since we're not doing building counts, we'll need to change this display
    #dict to economic loss by occupancy - perhaps "Building Loss" and "Content Loss"?
    econ_loss_occup = prepBuildingDamageOccup(hazus_results_dict['econ_loss_occup'])
    econ_loss_bldg_type = prepEconLossByType(hazus_results_dict['econ_loss_bldg_type'])
    hues = ['Building', 'Content', 'Total']
    econ_loss_occup_plot = prepBarPlot(econ_loss_occup, 'Occupancy', hues)
    econ_loss_bldg_type_plot = prepBarPlot(econ_loss_bldg_type, 'Type', hues)
    econ_loss_occup_plot['Occupancy'] = econ_loss_occup_plot['Type']
    

    # add new occupancy by building type dataframe to results
    hazus_results_dict.update({'econ_loss_occup_plot': econ_loss_occup_plot})
    hazus_results_dict.update({'econ_loss_bldg_type_plot': econ_loss_bldg_type_plot})

    # Join and group results dataframes into subcounty and county dataframes
    subcounty_results = hazus_results_dict['econ_loss'].join([hazus_results_dict['demographics'],
    hazus_results_dict['impact'], hazus_results_dict['censusblock_spatial']])
    subcounty_results = subcounty_results.drop(['Shape'], axis=1)
    subcounty_results['CensusBlock'] = subcounty_results.index
    subcounty_results = subcounty_results.merge(hazus_results_dict['county_fips'], on='Tract')
    county_results = subcounty_results.groupby(subcounty_results['CountyFips']).agg({
        'TotalLoss': 'sum',
        'BldgLoss': 'sum',
        'ContLoss': 'sum',
        'Population': 'sum',
        'Households': 'sum',
        'Debris': 'sum',
        'DisplPop': 'sum',
        'Shelter': 'sum',
        'CountyFips': 'first',
        'CountyName': 'first',
        'State': 'first'
    })
    
    #Summarize and export damaged essential facilities
    essential_facilities = ['CareFlty', 'EmergencyCtr', 'FireStation',
                            'PoliceStation', 'School', 'HighwayBridge', 
                            'LightRailBridge', 'RailwayBridge', 'ElectricPowerFlty',
                            'NaturalGasFlty', 'OilFlty', 'PotableWaterFlty', 
                            'PotableWaterPl', 'WasteWaterFlty']

    damaged_facilities = pd.DataFrame()
    damaged_facilities_shp = pd.DataFrame()
    
    for i in essential_facilities:
        print(i)
        name = 'fl' + 'FR' + i
        query = """SELECT * FROM %s.dbo.""" %inputs['study_region'] + name
        df = pd.read_sql(query, cnxn)
        dmg_column = [column for column in df.columns if 'Dmg' in column or 'Damage' in column]
        dmg_query = """SELECT * FROM %s.dbo.""" %inputs['study_region'] + name + """ WHERE """ + dmg_column[0] + """ > 0"""
        df = pd.read_sql(dmg_query, cnxn)
        if i == 'EmergencyCtr':
            ID = 'EocId'
        else:
            ID = i + 'Id'
        df = df.set_index(ID)
        df['Fac_Type'] = str(i)
        damaged_facilities = damaged_facilities.append(df)
        # Only export records from spatial table that correspond to records with economic loss in damage table
        if len(df.index) > 0:
            damage_ids = "', '".join(list(df.index))
            spatial = 'hz' + i
            columns_query = """SELECT COLUMN_NAME FROM """ + inputs['study_region'] + """.information_schema.columns
            WHERE TABLE_NAME = '""" + spatial + """' AND columns.COLUMN_NAME NOT IN('Shape')"""
            columns_df = pd.read_sql(columns_query, cnxn)
            columns = ",".join(list(columns_df.COLUMN_NAME))
            spatial_query = """SELECT """ + columns + """, Shape.STAsText() AS Shape FROM %s.dbo.""" %inputs['study_region'] + spatial + """ WHERE """ + ID + """ in ('""" + damage_ids + """')"""
            spatial_df = pd.read_sql(spatial_query, cnxn)
            ids = [id for id in spatial_df.columns if 'Id' in id]
            spatial_df = spatial_df.set_index(ids[0])
            results_df = spatial_df.join(df, on = ids[0], how = 'inner')
            # remove boolean data so gpd can parse to file
            # results_df = setValuesValid(results_df)
            # for result in results_df.columns:
            #     typeof = type(results_df[result].iloc[0])
            #     if (typeof == np.bool_) | (typeof == np.bool):
            #         results_df[result] = results_df[result].astype(int)
            #         results_df[result] = np.where(np.isnan(results_df[result]), 0, 1)
            #append essential facility layer to dataframe to turn to shp
            damaged_facilities_shp = damaged_facilities_shp.append(results_df)
            #Count offline essential facilities by county and add to county_results
            results_df['CountyFips'] = results_df['Tract'].str[:5]
            count_df = results_df[results_df.Functionality<1].groupby('CountyFips').count()
            count_df[i] = count_df['Functionality']
            # remove duplicate columns
            for col in count_df.columns:
                if col in list(county_results.columns):
                    count_df = count_df.drop(col, axis=1)
            county_results = county_results.join(count_df[i])

    # consolidates all data for validating values
    return_dict_update = {
        'subcounty_results': subcounty_results,
        'county_results': county_results,
        'damaged_facilities': damaged_facilities,
        'damaged_facilities_shp': damaged_facilities_shp
    }
    return_dict = hazus_results_dict.copy()
    return_dict.update(return_dict_update)
    # validate all values
    for k, v in return_dict.items():
        return_dict[k] = setValuesValid(v)

    if inputs['opt_shp']:
        try:
            damaged_facilities_shp['geometry'] = damaged_facilities_shp['Shape'].apply(loads)
            gdf = gpd.GeoDataFrame(damaged_facilities_shp, geometry = 'geometry')
            crs={'proj':'longlat', 'ellps':'WGS84', 'datum':'WGS84','no_defs':True}
            gdf.crs = crs
            geom_types = gdf['geometry'].apply(type).unique()
            if len(geom_types) > 1:
                for geom_type in geom_types:
                    gdf_new = gdf[gdf['geometry'].apply(type) == geom_type]
                    gdf_new.to_file(inputs['output_directory'] + '/' + inputs['study_region'] + '/damaged_facilities_' + str(geom_type).split('.')[2] + '.shp', driver='ESRI Shapefile')
            else:
                gdf.to_file(inputs['output_directory'] + '/' + inputs['study_region'] + '/damaged_facilities' + '.shp', driver='ESRI Shapefile')
        except:
            print('No damaged essential facility spatial data available')


    return hazus_results_dict, subcounty_results, county_results, damaged_facilities

#Export results dataframes to text files
def to_csv(hazus_results_dict, subcounty_results, county_results, damaged_facilities, inputs):
    tabular_df = {'econ_loss_occup':
                    hazus_results_dict['econ_loss_occup'],
                    'econ_loss_bldg_type':
                    hazus_results_dict['econ_loss_bldg_type'],
                    'censusblock_results': subcounty_results,
                    'county_results': county_results,
                    'damaged_facilities': damaged_facilities}
    json_output = {}
    for name, dataframe in tabular_df.items():
        if (not dataframe.empty) and (len(dataframe) > 0):
            path = inputs['output_directory'] + '\\' + inputs['study_region'] + '\\' + name + '.csv'
            if inputs['opt_csv']:
                dataframe.to_csv(path)
            if inputs['opt_json']:
                dataframe = dataframe.replace({pd.np.nan: 'null'})
                dictionary = dataframe.to_dict()
                json_output.update({name: dictionary})
    if inputs['opt_json']:
        with open(inputs['output_directory'] + '/' + inputs['study_region'] + '/' + inputs['study_region'] + '.json', 'w') as j:
            json.dump(json_output, j)

#Create shapefile of tract results table
def to_shp(inputs, hazus_results_dict, subcounty_results):
    if len(hazus_results_dict['econ_loss']) > 0:
        print('creating geodataframe')
        t0 = time()
        spatial_df = hazus_results_dict['censusblock_spatial'].drop(['Tract'], axis=1).reset_index()
        df = subcounty_results.merge(spatial_df, on='CensusBlock')
        df['geometry'] = df['Shape'].apply(loads)
        df.drop('Shape', axis=1)
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        crs={'proj':'longlat', 'ellps':'WGS84', 'datum':'WGS84','no_defs':True}
        gdf.crs = crs
        print(time() - t0)
        if inputs['opt_shp']:
            print('saving shapefile')
            t0 = time()
            gdf.to_file(inputs['output_directory'] + '/' + inputs['study_region'] + '/' + 'censusblock_results.shp', driver='ESRI Shapefile')
            print(time() - t0)
        return gdf
    else:
        sys.exit('No economic loss — unable to process study region')
