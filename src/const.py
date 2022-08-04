"""  
Constants and direct damages for Stix FAS

Angus Toms 
12 05 2021
"""
import csv
from typing import Dict, List

import os
import sys


def csv_to_dict(fname: str) -> Dict[int, List[float]]:
    """ Read .csv into dictionary. First row element added as key, rest of row added as value

    Args:
        fname (str): .csv file

    Returns:
        Dict[int, List[float]]: Dictionary containing .csv data
    """
    with open(fname) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        return {int(row[0]): [float(n) for n in row[1::]] for row in csv_reader}


def csv_to_list(fname: str) -> List[List]:
    """ Read .csv into 2d list
    """
    with open(fname) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        return [[float(n) if n else None for n in row] for row in csv_reader]


def get_resource_path(fname: str) -> str:
    """ Translate asset paths to useable format for pyinstaller
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, fname)

    return os.path.join(os.path.abspath('.'), fname)


"""
##########
RESIDENTIAL DIRECT DAMAGES
##########
"""
short_duration_no_warning = csv_to_dict(
    get_resource_path("tables/Short_Duration_No_Warning.csv"))
short_duration_less_warning = csv_to_dict(
    get_resource_path("tables/Short_Duration_Less_Warning.csv"))
short_duration_more_warning = csv_to_dict(
    get_resource_path("tables/Short_Duration_More_Warning.csv"))

long_duration_no_warning = csv_to_dict(
    get_resource_path("tables/Long_Duration_No_Warning.csv"))
long_duration_less_warning = csv_to_dict(
    get_resource_path("tables/Long_Duration_Less_Warning.csv"))
long_duration_more_warning = csv_to_dict(
    get_resource_path("tables/Long_Duration_More_Warning.csv"))

extra_long_duration_no_warning = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_No_Warning.csv"))
extra_long_duration_less_warning = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_Less_Warning.csv"))
extra_long_duration_more_warning = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_More_Warning.csv"))


"""
##########
NON-RESIDENTIAL DIRECT DAMAGES
##########
"""
# Non-Residential damage datasets
short_duration_no_warning_cellar = csv_to_dict(
    get_resource_path("tables/Short_Duration_No_Warning_Cellar.csv"))
short_duration_warning_cellar = csv_to_dict(
    get_resource_path("tables/Short_Duration_Warning_Cellar.csv"))
short_duration_no_warning_no_cellar = csv_to_dict(
    get_resource_path("tables/Short_Duration_No_Warning_No_Cellar.csv"))
short_duration_warning_no_cellar = csv_to_dict(
    get_resource_path("tables/Short_Duration_Warning_No_Cellar.csv"))

long_duration_no_warning_cellar = csv_to_dict(
    get_resource_path("tables/Long_Duration_No_Warning_Cellar.csv"))
long_duration_warning_cellar = csv_to_dict(
    get_resource_path("tables/Long_Duration_Warning_Cellar.csv"))
long_duration_no_warning_no_cellar = csv_to_dict(
    get_resource_path("tables/Long_Duration_No_Warning_No_Cellar.csv"))
long_duration_warning_no_cellar = csv_to_dict(
    get_resource_path("tables/Long_Duration_Warning_No_Cellar.csv"))

extra_long_duration_no_warning_cellar = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_No_Warning_Cellar.csv"))
extra_long_duration_warning_cellar = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_Warning_Cellar.csv"))
extra_long_duration_no_warning_no_cellar = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_No_Warning_No_Cellar.csv"))
extra_long_duration_warning_no_cellar = csv_to_dict(
    get_resource_path("tables/Extra_Long_Duration_Warning_No_Cellar.csv"))


"""
##########
EVAC COSTS DIRECT DAMAGES
##########
"""
high_evacuation = csv_to_dict(get_resource_path("tables/High_Evacuation.csv"))
mid_evacuation = csv_to_dict(get_resource_path("tables/Mid_Evacuation.csv"))
low_evacuation = csv_to_dict(get_resource_path("tables/Low_Evacuation.csv"))


"""
##########
TABLES
##########
"""
# Table A* - Initial return periods
initial_return_periods = [
    5,
    10,
    25,
    50,
    100,
    200
]

# Table A - Number of properties affected as pct of 200 year no.
props_affected = [
    5,
    10,
    25,
    80,
    93,
    100
]

# Table B - Location weightings
location_weightings = {
    "Rural": 1.107,
    "Urban": 1.056
}

# Table C - Average Annual Damage per res property
damage_per_res_prop = csv_to_list(
    get_resource_path("tables/Res_Damage_Per_Property.csv"))

# Table D - Average Annual Damage per non-res property
damage_per_non_res_prop = csv_to_list(
    get_resource_path("tables/Non_Res_damage_Per_Property.csv"))

# Table F1 - AEPS before
intangible_aeps_before = [0, 0.8, 1, 4/3, 2, 10/3, 5, 10, 100, 10**10]
# Table F2 - AEPS after
intangible_aeps_after = [0, 2/3, 0.8, 1, 4/3, 2, 10/3, 5, 10, 10**10]
# Table F - Direct intangible damages
intangible_direct_damages = csv_to_list(
    get_resource_path("tables/Intangible.csv"))
intangible_direct_damages_150 = [row[1] for row in intangible_direct_damages]

# Table G - Mental health costs
mental_health_costs = [0, 1878, 3028, 4136]

# Table H - Adults per propety
adults_per_property = {
    0: 1.85,
    11: 2.01,
    12: 2,
    13: 1.95,
    14: 1.99,
    15: 1.45
}

# Table I - Vehicle damage based on depth
vehicle_damages = [0, 3600]

# Table J - Flood Warning Weighting
weightings = [1, 0.75]


"""
##########
GENERAL
##########
"""
# Depths at which direct damage data is recorded for residential properties
residential_depths = [-0.3, 0, 0.05, 0.1, 0.2,
                      0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3]

# Depths at which direct damage data is recorded for non-res poperties
non_residential_depths = [-1, -0.75, -0.5, -0.25, 0, 0.25,
                          0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3]

# Depths at which direct damage data is recorded for evacuation costs
evacuation_depths = [0, 0.01, 0.1, 0.2, 0.3, 0.6, 1, 2]

# Headings for standard property tables
table_headings = [
    "Easting",
    "Northing",
    "Primary Address",
    "Secondary Address",
    "Town",
    "Postcode",
    "Floor Area",
    "MCM Code"
]

# Updated version of Table A* for overview appraisals
overview_return_periods = [
    2,
    5,
    10,
    25,
    50,
    100,
    200
]

# Used for display purpouses
initial_aeps = [
    "AEP: 20%",
    "AEP: 10%",
    "AEP: 4%",
    "AEP: 2%",
    "AEP: 1%",
    "AEP: 0.5%"
]
overview_aeps = [
    "AEP: 50%",
    "AEP: 20%",
    "AEP: 10%",
    "AEP: 4%",
    "AEP: 2%",
    "AEP: 1%",
    "AEP: 0.5%"
]

"""
##########
MCMs
##########
"""
non_res_mcm = {
    2: "Retail",
    3: "Offices",
    4: "Warehouses",
    51: "Leisure",
    521: "Playing Field",
    523: "Sports Centre",
    525: "Sports Stadium",
    526: "Marina",
    6: "Public Buildings",
    8: "Industry",
    910: "Car Park",
    960: "Substation",
    999: "Non-Residential Sector Average",
}

res_mcm = {
    0: "Residential Sector Average",
    11: "Detached",
    12: "Semi-Detached",
    13: "Terrace",
    14: "Bungalow",
    15: "Flat"
}

valid_mcms = [mcm for mcm in non_res_mcm] + [mcm for mcm in res_mcm]

# Different order and contains multi-story cp
overview_non_res_mcm = [
    "Retail",
    "Offices",
    "Warehouses",
    "Public Buildings",
    "Industry",
    "Leisure",
    "Playing Field",
    "Sports Centre",
    "Sports Stadium",
    "Marina",
    "Car Park",
    "Multi-storey Car Park",
    "Substation",
    "Non-Residential Sector Average"
]
