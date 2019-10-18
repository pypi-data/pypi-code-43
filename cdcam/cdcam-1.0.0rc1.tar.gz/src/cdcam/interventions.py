"""Decide on interventions
"""
# pylint: disable=C0103
from cdcam.model import PostcodeSector

import copy
import math

################################################################
# EXAMPLE COST LOOKUP TABLE
# - TODO come back to net present value or total cost of ownership for costs
################################################################

# Postcode-sector level individual interventions
INTERVENTIONS = {
    'upgrade_to_lte': {
        'name': 'Upgrade site to LTE',
        'description': 'If a site has only 2G/3G',
        'result': '800 and 2600 bands available',
        'cost': 142446,
        'assets_to_build': [
            {
                # site_ngr to match upgraded
                'site_ngr': None,
                'frequency': '800',
                'technology': 'LTE',
                'type': 'macrocell_site',
                'bandwidth': '2x10MHz',
                # set build date when deciding
                'build_date': None,
            },
            {
                # site_ngr to match upgraded
                'site_ngr': None,
                'frequency': '2600',
                'technology': 'LTE',
                'type': 'macrocell_site',
                'bandwidth': '2x10MHz',
                # set build date when deciding
                'build_date': None,
            },
        ]
    },
    'carrier_700': {
        'name': 'Build 700 MHz carrier',
        'description': 'Available if a site has LTE',
        'result': '700 band available',
        'cost': 50917,
        'assets_to_build': [
            {
                # site_ngr to match upgraded
                'site_ngr': None,
                'frequency': ['700'],
                'technology': '5G',
                'type': 'macrocell_site',
                'bandwidth': '2x10MHz',
                # set build date when deciding
                'build_date': None,
            },
        ]
    },
    'carrier_3500': {
        'name': 'Build 3500 MHz carrier',
        'description': 'Available if a site has LTE',
        'result': '3500 band available',
        'cost': 50917,
        'assets_to_build': [
            {
                # site_ngr to match upgraded
                'site_ngr': None,
                'frequency': ['3500'],
                'technology': '5G',
                'type': 'macrocell_site',
                'bandwidth': '2x10MHz',
                # set build date when deciding
                'build_date': None,
            },
        ]
    },
    'carrier_26000': {
        'name': 'Build 26000 MHz carrier',
        'description': 'Available if a site has LTE',
        'result': '26000 band available',
        'cost': 50917,
        'assets_to_build': [
            {
                # site_ngr to match upgraded
                'site_ngr': None,
                'frequency': ['260000'],
                'technology': '5G',
                'type': 'macrocell_site',
                'bandwidth': '2x100MHz',
                # set build date when deciding
                'build_date': None,
            },
        ]
    },
    'small_cell': {
        'name': 'Build a small cell',
        'description': 'Must be deployed at preset densities to be modelled',
        'result': '2x25 MHz small cells available at given density',
        'cost': 40220,
        'assets_to_build': [
            {
                # site_ngr not used
                'site_ngr': 'small_cell_site',
                'frequency': '3700',
                'technology': '5G',
                'type': 'small_cell',
                'bandwidth': '2x25MHz',
                # set build date when deciding
                'build_date': None,
            },
        ]
    },
}

AVAILABLE_STRATEGY_INTERVENTIONS = {
    # Intervention Strategy 1
    # Minimal Intervention 'Do Nothing Scenario'
    # Undertake no upgrades -> will lead to a capacity margin deficit
    # Capacity will be the sum of 800 and 2600 MHz
    'minimal': (),

    # Not a specific intervention strategy, but a foundational step in the
    # following strategies.
    'upgrade_to_lte': ('upgrade_to_lte'),

    # Intervention Strategy 2
    # Integrate 700, 3500 and 26000 MHz on to the macrocellular layer
    # The cost will be the addtion of another carrier on each basestation
    # (providing there is 4G already)
    # If 4G isn't present, the site will need major upgrades.
    'macrocell': ('upgrade_to_lte', 'carrier_700',
                  'carrier_3500', 'carrier_26000'),

    # Intervention Strategy 3
    # Deploy a small cell layer at 3700 MHz and 26 GHz
    # The cost will include the small cell unit and the civil works per cell
    'small-cell': ('upgrade_to_lte', 'small_cell'),

    # Intervention Strategy 4
    # Deploy a small cell layer at 3700 MHz and 26 GHz
    # The cost will include the small cell unit and the civil works per cell
    'small-cell-and-spectrum': ('upgrade_to_lte', 'carrier_700',
                   'carrier_3500', 'carrier_26000', 'small_cell'),
}


def decide_interventions(strategy, budget, service_obligation_capacity,
                         system, timestep, simulation_parameters):
    """
    Given a system and a set of strategy parameters, return the
    best selected interventions.

    Parameters
    ----------
    strategy : str
        One of 'minimal', 'macrocell', 'small_cell' intervention strategies.
    budget : int
        Annual budget in GBP.
    service_obligation_capacity : float
        Threshold for universal mobile service, in Mbps/km^2.
    system : NetworkManager
        Gives areas (postcode sectors) with population density, demand.
    timestep : int
        The current simulation timestep.
    simulation_parameters : dict
        All necessary simulation parameters.

    """
    available_interventions = AVAILABLE_STRATEGY_INTERVENTIONS[strategy]

    if service_obligation_capacity > 0:
        service_built, budget, service_spend = meet_service_obligation(budget,
            available_interventions, timestep, service_obligation_capacity, system, simulation_parameters)
    else:
        service_built = []
        service_spend = []

    built, budget, spend = meet_demand(
        budget, available_interventions, timestep, system, simulation_parameters)

    print("Service", len(service_built))
    print("Demand", len(built))

    return built + service_built, budget, spend + service_spend


def meet_service_obligation(budget, available_interventions, timestep,
    service_obligation_capacity, system, simulation_parameters):
    """
    Suggest areas based on meeting a desired capacity threshold.

    Parameters
    ----------
    budget : int
        Annual budget in GBP.
    available_interventions : tuple
        Contains the different intervention options that can be selected.
    timestep : int
        The current simulation timestep.
    service_obligation_capacity : float
        Threshold for universal mobile service, in Mbps/km^2.
    system : NetworkManager
        Gives areas (postcode sectors) with population density, demand.
    simulation_parameters : dict
        All necessary simulation parameters.

    """

    areas = _suggest_target_postcodes(system, service_obligation_capacity)

    return _suggest_interventions(budget, available_interventions,
        areas, timestep, simulation_parameters, service_obligation_capacity)


def meet_demand(budget, available_interventions, timestep, system,
    simulation_parameters):
    """
    Suggest areas based on meeting highest demand first.

    Parameters
    ----------
    budget : int
        Annual budget in GBP.
    available_interventions : tuple
        Contains the different intervention options that can be selected.
    timestep : int
        The current simulation timestep.
    system : NetworkManager
        Gives areas (postcode sectors) with population density, demand.
    simulation_parameters : dict
        All necessary simulation parameters.

    """
    areas = _suggest_target_postcodes(system)

    return _suggest_interventions(
        budget, available_interventions, areas, timestep, simulation_parameters)


def _suggest_interventions(budget, available_interventions, areas, timestep,
    simulation_parameters, threshold=None):
    """
    Suggest suitable interventions.

    Parameters
    ----------
    available_interventions : tuple
        Contains the different intervention options that can be selected.
    areas : List of objects
        Contains ranked list of postcode sector objects requiring upgrades.
    timestep : int
        The current simulation timestep.
    simulation_parameters : dict
        Contains all simulation parameters for the simulation
    threshold : int
        A target capacity value desired for each area.

    """
    built_interventions = []
    spend = []
    for area in areas:
        area_interventions = []
        if budget <= 0:
            break

        if _area_satisfied(area, area_interventions, threshold, simulation_parameters):
            continue

        # group assets by site
        assets_by_site = {}
        for asset in area.assets:
            if asset['site_ngr'] not in assets_by_site:
                assets_by_site[asset['site_ngr']] = [asset]
            else:
                assets_by_site[asset['site_ngr']].append(asset)

        # integrate_800 and integrate_2.6
        if 'upgrade_to_lte' in available_interventions:
            build_option = INTERVENTIONS['upgrade_to_lte']['assets_to_build']
            cost = INTERVENTIONS['upgrade_to_lte']['cost']
            for site_ngr, site_assets in assets_by_site.items():
                if site_ngr == 'small_cell_site':
                    continue
                if 'LTE' not in [asset['technology'] for asset in site_assets]:
                    # set both assets to this site_ngr
                    for option in build_option:
                        to_build = copy.copy(option)
                        to_build['site_ngr'] = site_ngr
                        to_build['pcd_sector'] = area.id
                        to_build['build_date'] = timestep
                        area_interventions.append(to_build)
                        built_interventions.append(to_build)

                    budget -= cost
                    spend.append((area.id, area.lad_id, 'upgrade_to_lte', cost))
                    if budget <= 0:
                        break

        if budget <= 0:
            break

        # integrate_700
        if 'carrier_700' in available_interventions and timestep >= 2020:
            if _area_satisfied(area, area_interventions, threshold, simulation_parameters):
                continue

            build_option = INTERVENTIONS['carrier_700']['assets_to_build']
            cost = INTERVENTIONS['carrier_700']['cost']
            for site_ngr, site_assets in assets_by_site.items():
                if site_ngr == 'small_cell_site':
                    continue
                if 'LTE' in [asset['technology'] for asset in site_assets] and \
                        '700' not in [asset['frequency'] for asset in site_assets]:
                    # set both assets to this site_ngr
                    for option in build_option:
                        to_build = copy.copy(option)
                        to_build['site_ngr'] = site_ngr
                        to_build['pcd_sector'] = area.id
                        to_build['build_date'] = timestep
                        area_interventions.append(to_build)
                        built_interventions.append(to_build)

                    spend.append((area.id, area.lad_id, 'carrier_700', cost))
                    budget -= cost
                    if budget <= 0:
                        break

        if budget <= 0:
            break

        # integrate_3.5
        if 'carrier_3500' in available_interventions and timestep >= 2020:
            if _area_satisfied(area, area_interventions, threshold, simulation_parameters):
                continue

            build_option = INTERVENTIONS['carrier_3500']['assets_to_build']
            cost = INTERVENTIONS['carrier_3500']['cost']
            for site_ngr, site_assets in assets_by_site.items():
                if site_ngr == 'small_cell_site':
                    continue
                if 'LTE' in [asset['technology'] for asset in site_assets] and \
                        '3500' not in [asset['frequency'] for asset in site_assets]:
                    # set both assets to this site_ngr
                    for option in build_option:
                        to_build = copy.copy(option)
                        to_build['site_ngr'] = site_ngr
                        to_build['pcd_sector'] = area.id
                        to_build['build_date'] = timestep
                        area_interventions.append(to_build)
                        built_interventions.append(to_build)

                    spend.append((area.id, area.lad_id, 'carrier_3500', cost))
                    budget -= cost
                    if budget <= 0:
                        break

        if budget <= 0:
            break

        if 'carrier_26000' in available_interventions and timestep >= 2020:
            if not area.clutter_environment == 'urban':
                continue

            if _area_satisfied(area, area_interventions, threshold, simulation_parameters):
                continue

            build_option = INTERVENTIONS['carrier_26000']['assets_to_build']
            cost = INTERVENTIONS['carrier_26000']['cost']
            for site_ngr, site_assets in assets_by_site.items():
                if site_ngr == 'small_cell_site':
                    continue

                if 'LTE' in [asset['technology'] for asset in site_assets] and \
                        '26000' not in [asset['frequency'] for asset in site_assets]:

                    # set both assets to this site_ngr
                    for option in build_option:
                        to_build = copy.copy(option)
                        to_build['site_ngr'] = site_ngr
                        to_build['pcd_sector'] = area.id
                        to_build['build_date'] = timestep
                        area_interventions.append(to_build)
                        built_interventions.append(to_build)

                    spend.append((area.id, area.lad_id, 'carrier_26000', cost))
                    budget -= cost
                    if budget <= 0:
                        break

        if budget <= 0:
            break

        # build small cells to next density
        if 'small_cell' in available_interventions and timestep >= 2020:

            if area.clutter_environment == 'rural':
                continue

            if _area_satisfied(area, area_interventions, threshold, simulation_parameters):
                continue

            build_option = INTERVENTIONS['small_cell']['assets_to_build']
            cost = INTERVENTIONS['small_cell']['cost']

            loop_number = 0
            while True:

                to_build = copy.deepcopy(build_option)
                to_build[0]['build_date'] = timestep
                to_build[0]['pcd_sector'] = area.id

                area_interventions += to_build
                built_interventions += to_build
                spend.append((area.id, area.lad_id, 'small_cells', cost))
                budget -= cost

                loop_number += 1

                if _area_satisfied(area, area_interventions, threshold, simulation_parameters):
                    break

                if budget <= 0:
                    break

    return built_interventions, budget, spend


def _suggest_target_postcodes(system, threshold=None):
    """
    Sort postcodes by population density (descending)
    - if considering threshold, filter out any with capacity above threshold.

    """
    postcodes = system.postcode_sectors.values()

    if threshold is not None:
        considered_postcodes = [pcd for pcd in postcodes if pcd.capacity < threshold]
    else:
        considered_postcodes = [p for p in postcodes]

    return sorted(considered_postcodes, key=lambda pcd: -pcd.population_density)


def _area_satisfied(area, built_interventions, threshold, simulation_parameters):
    """
    Check if area demand has been satisfied by current capacity.

    """
    if threshold is None:
        target_capacity = area.demand
    else:
        target_capacity = threshold

    data = {
        "id": area.id,
        "lad_id": area.lad_id,
        "population": area.population,
        "area_km2": area.area,
        "user_throughput": area.user_throughput,
    }

    assets = area.assets + built_interventions

    test_area = PostcodeSector(
        data,
        assets,
        area._capacity_lookup_table,
        area._clutter_lookup,
        simulation_parameters,
    )

    reached_capacity = test_area.capacity

    return reached_capacity >= target_capacity
