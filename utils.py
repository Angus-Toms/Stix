
import csv
import json
import math
from typing import Any, Dict, List, Union

import os
import sys

import numpy as np
import xlsxwriter
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QItemDelegate, QLineEdit,
                             QStyledItemDelegate, QWidget)

import const

"""
LAYOUTS
"""


def centered_hbox(widget: QWidget) -> QHBoxLayout:
    """ Centers widget in a horizontal layout

    Args:
        widget (QWidget): Widget to be centered

    Returns:
        QHBoxLayout: Widget within horizontal layour
    """
    hbox = QHBoxLayout()
    hbox.addStretch()
    hbox.addWidget(widget)
    hbox.addStretch()

    return hbox


def centered_hbox_lyt(lyt: QHBoxLayout) -> QHBoxLayout:
    """ Centers layout in a horizontal layout
    
    Args:
        lyt (QHBoxLayout): Layout to be centered 
        
    Returns:
        QHBoxLayout: Layout centered within horizontal layout
    """
    hbox = QHBoxLayout()
    hbox.addStretch()
    hbox.addLayout(lyt)
    hbox.addStretch()

    return hbox


""" 
FILE DIALOGS
"""


def get_save_fname(parent: QWidget) -> str:
    """ Run a save file dialog box
    
    Args:
        parent (QWidget): Widget from which to run dialog
        
    Returns:
        str: Filename with file type discarded
    
    """
    return QFileDialog.getSaveFileName(parent, "Select Save Location")[0]




"""
GENERAL
"""

def is_valid_res(prop_details: List) -> bool:
    """ Check whether property details entered are all valid.
    Entries must be able to be parsed to the following:
    - arg[0]: Easting (float)
    - arg[1]: Northing (float)
    - arg[2]: Primary address (str)
    - arg[3]: Secondary address (str)
    - arg[4]: Town (str)
    - arg[5]: Postcode (str)
    - arg[6]: Floor area 
    ** Don't need to actually test FA but it just makes everything a little easier later **
    - arg[7]: MCM code (int)
    
    Args:
        prop_details (List): Details of property in the above order
        
    Returns:
        bool: True if property is valid, False otherwise
    """
    # Test entry types
    expected_types = [float, float, str, str, str, str, None, int]
    for i in range(len(expected_types)):

        # Skip FA entry
        if i == 6:
            continue

        try:
            expected_types[i](prop_details[i])
        except:
            return False

    # Test MCM
    return int(prop_details[7]) in const.res_mcm


def is_valid_non_res(prop_details: List) -> bool:
    """ Check whether property details entered are all valid. 
    Entries must be able to be parsed to the following:
    - arg[0]: Easting (float)
    - arg[1]: Northing (float)
    - arg[2]: Primary address (str)
    - arg[3]: Secondary address (str)
    - arg[4]: Town (str)
    - arg[5]: Postcode (str)
    - arg[6]: Floor Area (float)
    - arg[7]: MCM code (int)
    
    Args:
        prop_details (List): Details of property in the above order
        
    Returns:
        bool: True if property is valid, False otherwise
    """
    # Test entry types
    expected_types = [float, float, str, str, str, str, float, int]
    for i in range(len(expected_types)):
        try:
            expected_types[i](prop_details[i])

        except:
            return False

    # Test MCM
    return int(prop_details[7]) in const.non_res_mcm


def is_valid_node(node_details: List) -> bool:
    """ Test information submitted about a node 
    All datapoints are depths or locations so should be floats
    
    Args:
        node_details (List): Details of node
        
    Returns:
        bool: True if node is valid, False otherwise
    """
    try:
        _ = [float(n) for n in node_details]
        return True

    except:
        return False


def is_valid_ascii(ascii_details: List) -> bool:
    """ Test information submitted about an ASCII grid
    All datapoints except fname should be floats
    
    Args:
        ascii_details (List): Details of ASCII grid 
        
    Returns:
        bool: True if grid is valid, False otherwise
    """
    try:
        [float(x) for x in ascii_details[1::]]
        return True

    except:
        return False


def get_resource_path(fname: str) -> str:
    """
    Translate asset paths to useable format for pyinstaller
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.abspath(sys._MEIPASS), fname)

    return os.path.join(os.path.abspath('.'), fname)

"""
TODO: MOVE FOLLOWING TO APPRAISAL SUPERCLASS 
"""

def get_damage_per_prop(warning: str) -> List[float]:
    """
    Return average annual direct damages based on flood warning
    """
    damages = const.damage_per_res_prop
    warning_dict = {
        "No Warning": damages[0],
        "Less than 8 hours": damages[1],
        "More than 8 hours": damages[2]
    }

    return warning_dict[warning]


def get_location_weight(location: str) -> float:
    """
    Return location weighting
    """
    return const.location_weightings[location]


def get_cumulative_props_at_risk(prop_count: int) -> List[float]:
    """
    Find cumulative properties at risk for varying return periods
    """
    return [prop_count * (i/93) for i in const.props_affected]


"""
DAMAGES
"""


def get_discount_factor(year: int) -> float:
    """
    Calculates df for a given year, potentially need to clean up some of the maths
    """
    if year < 30:
        return ((1/1.035)**year)

    if year < 75:
        return ((1/1.035)**30) * ((1/1.03)**(year-30))

    if year <= 100:
        return ((1/1.035)**30) * ((1/1.03)**45) * ((1/1.025)**(year-75))


def get_cumulative_discount_factor(year: int) -> float:
    """
    Sum of all dfs from 0 to year
    """
    return sum([get_discount_factor(y) for y in range(year+1)])


def get_health_discount_factor(year: int) -> float:
    """
    Calculate "risk to health and life" discount factor for a given year
    """
    if year < 30:
        return ((1/1.015)**year)

    if year < 75:
        return ((1/1.015)**30) * ((1/1.01286)**(year-30))

    if year <= 100:
        return ((1/1.015)**30) * ((1/1.01286)**45) * ((1/1.01071)**(year-75))


def get_cumulative_health_discount_factor(year: int) -> float:
    """
    Sum all dfs from 0 to year
    """
    return sum([get_health_discount_factor(y) for y in range(year+1)])


def apply_checks(checks: List[bool], datapoints: List) -> List:
    """
    Filter items in datapoints based on the state of the corresponsing check
    Used to remove datapoints of unselected properties and nodes
    """
    return [datapoints[i] for i in range(len(checks)) if checks[i]]


def get_res_event_damages(event_type: str) -> Dict[int, List]:
    """
    Return direct damages (from const.py)
    """
    dd = {
        "Short Duration Major Flood Storm No Warning": const.short_duration_no_warning,
        "Short Duration Major Flood Storm <8hr Warning": const.short_duration_less_warning,
        "Short Duration Major Flood Storm >8hr Warning": const.short_duration_more_warning,
        "Long Duration Major Flood Storm No Warning": const.long_duration_no_warning,
        "Long Duration Major Flood Storm <8hr Warning": const.long_duration_less_warning,
        "Long Duration Major Flood Storm >8hr Warning": const.long_duration_more_warning,
        "Extra-Long Duration Major Flood Storm No Warning": const.extra_long_duration_no_warning,
        "Extra-Long Duration Major Flood Storm <8hr Warning": const.extra_long_duration_less_warning,
        "Extra-Long Duration Major Flood Storm >8hr Warning": const.extra_long_duration_more_warning
    }

    return dd[event_type]


def get_non_res_event_damages(event_type: str, cellar: bool) -> Dict[int, List[float]]:
    """
    Find direct damage dict based on general flood information
    """
    durations = {
        "Short Duration Major Flood Storm No Warning": "sn",
        "Short Duration Major Flood Storm <8hr Warning": "sw",
        "Short Duration Major Flood Storm >8hr Warning": "sw",
        "Long Duration Major Flood Storm No Warning": "ln",
        "Long Duration Major Flood Storm <8hr Warning": "lw",
        "Long Duration Major Flood Storm >8hr Warning": "lw",
        "Extra-Long Duration Major Flood Storm No Warning": "en",
        "Extra-Long Duration Major Flood Storm <8hr Warning": "ew",
        "Extra-Long Duration Major Flood Storm >8hr Warning": "ew"
    }

    event_code = durations[event_type]
    event_code += "c" if cellar else "nc"

    direct_damages = {
        "snc": const.short_duration_no_warning_cellar,
        "snnc": const.short_duration_no_warning_no_cellar,
        "swc": const.short_duration_warning_cellar,
        "swnc": const.short_duration_warning_no_cellar,
        "lnc": const.long_duration_no_warning_cellar,
        "lnnc": const.long_duration_no_warning_no_cellar,
        "lwc": const.long_duration_warning_cellar,
        "lwnc": const.long_duration_warning_no_cellar,
        "enc": const.extra_long_duration_no_warning_cellar,
        "ennc": const.extra_long_duration_no_warning_no_cellar,
        "ewc": const.extra_long_duration_warning_cellar,
        "ewnc": const.extra_long_duration_warning_no_cellar
    }

    return direct_damages[event_code]


def get_nearest_node(property_e: float, property_n: float, nodes: zip) -> int:
    """
    Returns index of nearest node to a given property
    """
    node_lst = list(nodes)
    min_distance = math.sqrt(
        (property_e - node_lst[0][0])**2 + (property_n - node_lst[0][1])**2)
    min_index = 0

    for i in range(1, len(node_lst)):
        distance = math.sqrt(
            (property_e - node_lst[i][0])**2 + (property_n - node_lst[i][1])**2)
        if distance < min_distance:
            min_distance = distance
            min_index = i

    return min_index


def interpolate_res_damages(direct_damages: List[float], depths: List[float]) -> List[float]:
    """
    Interpolate damages based on depths
    """
    measured_depths = const.residential_depths
    damages = []

    for depth in depths:
        # Depth less than -.3, no damages
        if depth < -0.3:
            damages.append(0)

        # Depth greater than 3, max damage
        elif depth >= 3:
            damages.append(direct_damages[-1])

        else:
            i = 0
            while depth >= measured_depths[i]:
                i += 1

            # Find damage bounds
            total_damage_diff = direct_damages[i] - direct_damages[i-1]

            # Find depth bounds and interpolate
            actual_depth_diff = depth - measured_depths[i-1]
            total_depth_diff = measured_depths[i] - measured_depths[i-1]
            depth_diff_pct = actual_depth_diff / total_depth_diff

            damages.append(direct_damages[i-1] +
                           (depth_diff_pct * total_damage_diff))

    return damages


def interpolate_non_res_damages(direct_damages: List[float], depths: List[float]) -> List[float]:
    """
    Interpolate damages based on depths
    """
    measured_depths = const.non_residential_depths
    damages = []

    for depth in depths:
        # Depth less than -1, no damages
        if depth < -1:
            damages.append(0)

        # Depth greater than 3, max damage
        elif depth >= 3:
            damages.append(direct_damages[-1])

        # Interpolation
        else:
            i = 0
            while depth >= measured_depths[i]:
                i += 1

            # Find damage bounds
            total_damage_diff = direct_damages[i] - direct_damages[i-1]

            # Find depth bounds and interpolate
            actual_depth_diff = depth - measured_depths[i-1]
            total_depth_diff = measured_depths[i] - measured_depths[i-1]
            depth_diff_pct = actual_depth_diff / total_depth_diff

            damages.append(direct_damages[i-1] +
                           (depth_diff_pct * total_damage_diff))

    return damages


def get_average_annual(flood_events: List[int], event_damages: List[float]) -> float:
    """
    Find average annual damage using trapezium rule
    arg lists should be same length
    flood_events should be expressed as arps not aeps
    """
    aeps = [(1/event) for event in flood_events]
    event_count = len(flood_events)

    # Apply trapezium rule
    return sum([((event_damages[i]+event_damages[i+1]) * (aeps[i]-aeps[i+1]) / 2) for i in range(event_count-1)])


def get_capping_depth(flood_events: List[int], depths: List[float], damages: List[float], cap: float, df: float) -> Union[float, None]:
    """
    Find depth at which damages exceed damage cap
    """
    lifetime_damage = get_average_annual(flood_events, damages) * df
    # Damage cap not exceeded so capping depth doesn't exist
    if lifetime_damage < cap:
        return None

    target_damage = cap / df
    aeps = [1/event for event in flood_events]
    event_count = len(flood_events)

    trapezia = [((damages[i]+damages[i+1])*(aeps[i]-aeps[i+1])) /
                2 for i in range(event_count-1)]
    cumulative_damages = trapezia
    for i in range(1, event_count-1):
        cumulative_damages[i] += cumulative_damages[i-1]

    # Capped damage less than first damage reading so interpolation is not possible
    if target_damage < cumulative_damages[0]:
        return cumulative_damages[0]

    # Interpolation
    i = 0
    while cumulative_damages[i] < target_damage:
        i += 1

    damage_difference = (target_damage - cumulative_damages[i-1]) / (
        cumulative_damages[i] - cumulative_damages[i-1])
    depth_difference = depths[i] - depths[i-1]

    return depths[i-1] + (damage_difference * depth_difference)

# Intangible damages


def get_current_sop(flood_events: List[int], depths: List[float]) -> Union[float, None]:
    """
    Get first flood event during which damage occurs
    Return AEP
    """
    # Damage occurs when depth >= -0.3
    for i in range(len(depths)):
        if depths[i] >= -0.3:
            return (100/flood_events[i])


def get_intangible_damage(sop: Union[int, None]) -> float:
    """
    Get intangible damages 
    sop should be expressed as AEP *not* ARP
    """
    measured_aeps = const.intangible_aeps_before
    direct_damages = const.intangible_direct_damages_150

    # If property experiences no damage at any flood event then sop will be None
    # Intangible damages are always 0 in this case
    if sop is None:
        return 0

    # AEP higher than measured values, max damage
    if sop >= 100:
        return 303

    # AEP lower than measured values, no damage
    if sop <= 0:
        return 0

    # Interpolate
    i = 0
    while sop >= measured_aeps[i]:
        i += 1

    # Find damage bounds
    total_damage_diff = direct_damages[i] - direct_damages[i-1]

    # Find aep bounds and interpolate
    actual_aep_diff = sop - measured_aeps[i-1]
    total_aep_diff = measured_aeps[i] - measured_aeps[i-1]
    aep_diff_pct = actual_aep_diff / total_aep_diff

    return direct_damages[i-1] + (aep_diff_pct * total_damage_diff)


def get_intangible_benefit(aep_before: float, aep_after: int) -> float:
    """
    Bilinear interpolation
    Both args should be expressed as aep not arp
    """
    measured_aeps_before = const.intangible_aeps_before
    measured_aeps_after = const.intangible_aeps_after
    direct_damages = const.intangible_direct_damages

    if aep_before is None:
        return 0

    i, j = 0, 0

    while measured_aeps_after[i] < aep_after:
        i += 1

    while measured_aeps_before[j] < aep_before:
        j += 1

    top_left = direct_damages[j-1][i-1]
    top_right = direct_damages[j-1][i]
    bottom_left = direct_damages[j][i-1]
    bottom_right = direct_damages[j][i]

    if top_left is None or top_right is None or bottom_left is None or bottom_right is None:
        return 0

    x1 = measured_aeps_after[i-1]
    x2 = measured_aeps_after[i]
    y1 = measured_aeps_before[j-1]
    y2 = measured_aeps_before[j]

    coeff_1 = ((x2 - aep_after) * (y2 - aep_before)) / ((x2 - x1) * (y2 - y1))
    coeff_2 = ((aep_after - x1) * (y2 - aep_before)) / ((x2 - x1) * (y2 - y1))
    coeff_3 = ((x2 - aep_after) * (aep_before - y1)) / ((x2 - x1) * (y2 - y1))
    coeff_4 = ((aep_after - x1) * (aep_before - y1)) / ((x2 - x1) * (y2 - y1))

    return (coeff_1 * top_left) + (coeff_2 * top_right) + (coeff_3 * bottom_left) + (coeff_4 * bottom_right)

# Mental health costs


def get_mh_cost_per_depth(depth: float) -> int:
    """
    Get mh cost per adult for a given depth
    """
    direct_damages = const.mental_health_costs

    if depth < 0:
        return direct_damages[0]
    if depth <= 0.3:
        return direct_damages[1]
    if depth <= 1:
        return direct_damages[2]

    return direct_damages[3]


def get_mh_costs(depths: List[float], mcm: int) -> List[float]:
    """
    Get mental health costs for given depths and property type
    """
    adults = const.adults_per_property[mcm]
    return [(get_mh_cost_per_depth(depth) * adults) for depth in depths]

# Vehicular damages


def get_vehicular_damage_per_depth(depth: float) -> int:
    """
    Get vehicular damage for a given depth
    .15m added to depth to adjust for internal property threshold
    """
    if depth + 0.15 > 0.35:
        return const.vehicle_damages[1]

    return const.vehicle_damages[0]


def get_vehicle_damages(depths: List[float], weighting: float) -> List[float]:
    """
    Get vehicle damages for given depths and flood type
    """
    return [(get_vehicular_damage_per_depth(depth) * weighting) for depth in depths]

# Evacuation costs


def get_evac_category_costs(category: str) -> Dict[int, List[float]]:
    """
    Get evacuation direct costs (from tables.py)
    """
    costs = {
        "Low": const.low_evacuation,
        "Mid": const.mid_evacuation,
        "High": const.high_evacuation
    }

    return costs[category]


def get_evac_costs(evac_costs: List[float], depths: List[float]) -> List[float]:
    """
    Get evac costs for given depths and direct evac costs
    """
    measured_depths = const.evacuation_depths
    costs = []

    for depth in depths:
        # Depth less than 0, no cost
        if depth < 0:
            costs.append(0)

        # Depth grater than 2, max costs
        elif depth >= 2:
            costs.append(evac_costs[-1])

        # Interpolate
        else:
            i = 0
            while depth >= measured_depths[i]:
                i += 1

            total_damage_diff = evac_costs[i] - evac_costs[i-1]
            actual_depth_diff = depth - measured_depths[i-1]
            total_depth_diff = measured_depths[i] - measured_depths[i-1]
            depth_diff_pct = actual_depth_diff / total_depth_diff

            costs.append(evac_costs[i-1] +
                         (depth_diff_pct * total_damage_diff))

    return costs

# Emergency services


def get_location_weight(location: str) -> float:
    """
    Return emergency services weighting for arg location
    """
    return const.location_weightings[location]


"""
BENEFITS
"""


def get_benefits(flood_events: List[int], damages: List[int]) -> List[int]:
    """
    Perform trapezium rule on damages and aeps to get benefits
    """
    aeps = [(1/flood_event) for flood_event in flood_events]
    event_count = len(flood_events)

    # Perform trapezium rule
    trapezia = [(damages[i]+damages[i+1]) * (aeps[i]-aeps[i+1]) /
                2 for i in range(event_count-1)]
    return list(np.cumsum(trapezia))


def get_current_benefit(flood_events: List[int], benefits: List[float], sop: int) -> float:
    """
    Find current benefit from proposed SOP and list of benefits per return period
    """
    for i in range(len(flood_events)):
        if flood_events[i] == sop:
            return benefits[i]

    # SOP entered doesn't match any return period
    return 0


"""
FILE WRITING
"""


def list_to_csv(data: List[List], fname: str) -> None:
    """
    Write the contents of a 2d list to a .csv file with arg filename
    """
    with open(get_resource_path(fname), 'w') as csv_file:
        writer = csv.writer(csv_file)
        for row in data:
            clean_row = []
            for i in range(len(row)):
                try:
                    clean_row.append(round(row[i], 4))
                except:
                    clean_row.append(row[i])

            writer.writerow(clean_row)


def list_to_xlsx(data: List[List], fname: str) -> None:
    """
    Write the contents of a 2d list to a .xlsx file with arg filename
    """
    workbook = xlsxwriter.Workbook(get_resource_path(fname))
    worksheet = workbook.add_worksheet()

    for i in range(len(data)):
        for j in range(len(data[0])):
            try:
                worksheet.write(i, j, round(data[i][j], 4))
            except:
                worksheet.write(i, j, data[i][j])

    workbook.close()


def write_method_caveats(appraisal_type: str, fname: str) -> None:
    """
    Write .txt file containing str
    """
    from help_page_texts import (detailed_methodology_notes, initial_methodology_notes,
                                 overview_methodology_notes, detailed_caveats, initial_caveats, overview_caveats)

    if appraisal_type == "initial":
        with open(get_resource_path(fname), "w") as f:
            f.write("Methodology Notes \n\n" + initial_methodology_notes)
            f.write("\n\nCaveats \n\n" + initial_caveats)

    elif appraisal_type == "overview":
        with open(get_resource_path(fname), "w") as f:
            f.write("Methodology Notes \n\n" + overview_methodology_notes)
            f.write("\n\nCaveats \n\n" + overview_caveats)

    elif appraisal_type == "detailed":
        with open(get_resource_path(fname), "w") as f:
            f.write("Methodology Notes \n\n" + detailed_methodology_notes)
            f.write("\n\nCaveats \n\n" + detailed_caveats)


"""
CLASSES
"""


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index) -> None:
        return


class NumpyEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, np.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)


class IntegerDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        w = QLineEdit(parent)
        w.setInputMask("ddd")
        return w