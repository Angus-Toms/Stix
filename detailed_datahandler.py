import json
import os
import re
from linecache import getline
from typing import List

import numpy as np
from PyQt5.QtWidgets import QTableWidget

import utils 

class DetailedDataHandler():
    """
    Methods for the upload / storage / deletion / editing / processing and saving of
    data used in Detailed Appraisals
    """
    def __init__(self) -> None:
        # Residential information
        self.res_eastings = []
        self.res_northings = []
        self.res_addresses = []
        self.res_postcodes = []
        self.res_towns = []
        self.res_mcms = []
        self.res_ground_levels = []

        # Non-Residential information
        self.non_res_eastings = []
        self.non_res_northings = []
        self.non_res_addresses = []
        self.non_res_postcodes = []
        self.non_res_towns = []
        self.non_res_mcms = []
        self.non_res_floor_areas = []
        self.non_res_ground_levels = []

        # Node information
        self.node_eastings = []
        self.node_northings = []
        self.node_depths = []

        # ASCII information
        self.ascii_fnames = []
        self.n_cols = []
        self.n_rows = []
        self.x_corners = []
        self.y_corners = []
        self.cellsizes = []
        self.nodata_values = []
        self.raster_points = []

        # Upload counts
        self.res_count = 0
        self.non_res_count = 0
        self.node_count = 0
        self.ascii_count = 0

        # General flood info
        self.df = 0
        self.health_df = 0
        self.event_type = "Long Duration Major Flood Storm <8hr Warning"
        self.evac_cost_category = "High"
        self.location = "Rural"
        self.scheme_lifetime = 50
        self.sop = 25
        self.cellar = False
        self.caps_enabled = True
        self.res_cap = 250000
        self.non_res_cap = 260000
        self.return_periods = [5, 10, 25, 50, 100, 150, 1000]

        # Checks
        self.res_checks = []
        self.non_res_checks = []
        self.node_checks = []

        # Clean residential fields
        self.clean_res_e = []
        self.clean_res_n = []
        self.clean_res_m = []
        self.clean_res_gl = []
        self.clean_res_a = []
        self.clean_res_count = 0

        # Clean non-residential fields
        self.clean_non_res_e = []
        self.clean_non_res_n = []
        self.clean_non_res_m = []
        self.clean_non_res_a = []
        self.clean_non_res_gl = []
        self.clean_non_res_fa = []
        self.clean_non_res_count = 0

        # Clean node fields
        self.clean_node_e = []
        self.clean_node_n = []
        self.clean_node_d = []
        self.clean_node_count = 0

        # Residential results fields
        self.res_depths = []
        self.capped_res_depths = []
        self.res_damages = []
        self.capped_res_damages = []
        self.average_annual_damage_per_res = []
        self.lifetime_damage_per_res = []
        self.capped_average_annual_damage_per_res = []
        self.capped_lifetime_damage_per_res = []
        self.total_average_res_damage = 0
        self.total_lifetime_res_damage = 0
        self.res_benefits = []
        self.total_res_benefits = [0] * (len(self.return_periods) - 1)

        # Non-Residential results fields
        self.non_res_depths = []
        self.capped_non_res_depths = []
        self.non_res_damages = []
        self.capped_non_res_damages = []
        self.average_annual_damage_per_non_res = []
        self.lifetime_damage_per_non_res = []
        self.capped_average_annual_damage_per_non_res = []
        self.capped_lifetime_damage_per_non_res = []
        self.total_average_non_res_damage = 0
        self.total_lifetime_non_res_damage = 0
        self.non_res_benefits = []
        self.total_non_res_benefits = [0] * (len(self.return_periods) - 1)

        # Intangible results fields
        self.current_sops = []
        self.average_annual_intangible_damages = []
        self.lifetime_intangible_damages = []
        self.total_average_intangible_damage = 0
        self.total_lifetime_intangible_damage = 0
        self.annual_intangible_benefits = []
        self.lifetime_intangible_benefits = []

        # Mental health results fields
        self.mh_costs = []
        self.average_annual_mh_costs = []
        self.lifetime_mh_costs = []
        self.total_average_mh_costs = 0
        self.total_lifetime_mh_costs = 0
        self.mh_benefits = []
        self.total_mh_benefits = [0] * (len(self.return_periods) - 1)

        # Vehicular results fields
        self.vehicular_damages = []
        self.average_annual_vehicular_damages = []
        self.lifetime_vehicular_damages = []
        self.total_average_vehicular_damages = 0
        self.total_lifetime_vehicular_damages = 0
        self.vehicular_benefits = []
        self.total_vehicular_benefits = [0] * (len(self.return_periods) - 1)

        # Evacuation results fields
        self.evac_costs = []
        self.average_annual_evac_costs = []
        self.lifetime_evac_costs = []
        self.total_average_evac_costs = 0
        self.total_lifetime_evac_costs = 0
        self.evac_benefits = []
        self.total_evac_benefits = [0] * (len(self.return_periods) - 1)

        # Business disruption fields
        self.total_average_disruption = 0
        self.total_lifetime_disruption = 0

        # Infrastructure results fields
        self.total_average_infrastructure_damage = 0
        self.total_lifetime_infrastructure_damage = 0

        # Emergency services results fields
        self.total_average_emergency_services_costs = 0
        self.total_lifetime_emergency_services_costs = 0

        # Annual post-intervention damage fields
        self.annual_res_damage_after = 0
        self.annual_intangible_damage_after = 0
        self.annual_mh_damage_after = 0
        self.annual_vehicle_damage_after = 0
        self.annual_evac_damage_after = 0
        self.annual_non_res_damage_after = 0
        self.annual_disruption_after = 0
        self.annual_infrastructure_damage_after = 0
        self.annual_emergency_services_cost_after = 0

        # Lifetime post-intervention damage fields
        self.lifetime_res_damage_after = 0
        self.lifetime_intangible_damage_after = 0
        self.lifetime_mh_damage_after = 0
        self.lifetime_vehicle_damage_after = 0
        self.lifetime_evac_damage_after = 0
        self.lifetime_non_res_damage_after = 0
        self.lifetime_disruption_after = 0
        self.lifetime_infrastructure_damage_after = 0
        self.lifetime_emergency_services_cost_after = 0

        # Current SOP annual benefits fields
        self.current_annual_res_benefit = 0
        self.current_annual_intangible_benefit = 0
        self.current_annual_mh_benefit = 0
        self.current_annual_vehicle_benefit = 0
        self.current_annual_evac_benefit = 0
        self.current_annual_non_res_benefit = 0
        self.current_annual_disruption_benefit = 0
        self.current_annual_infrastructure_benefit = 0
        self.current_annual_emergency_services_benefit = 0

        # Current SOP lifetime benefits fields
        self.current_lifetime_res_benefit = 0
        self.current_lifetime_intangible_benefit = 0
        self.current_lifetime_mh_benefit = 0
        self.current_lifetime_vehicle_benefit = 0
        self.current_lifetime_evac_benefit = 0
        self.current_lifetime_non_res_benefit = 0
        self.current_lifetime_disruption_benefit = 0
        self.current_lifetime_infrastructure_benefit = 0
        self.current_lifetime_emergency_services_benefit = 0

        # Totals
        self.total_average_annual_damage = 0
        self.total_lifetime_damage = 0
        self.total_annual_damage_after = 0
        self.total_lifetime_damage_after = 0
        self.total_current_annual_benefit = 0
        self.total_current_lifetime_benefit = 0

    """
    UPLOAD/DELETION/EDITING METHODS
    """

    def add_prop(self, prop_details: List[str]) -> None:
        """ Add property details (if valid) to data handler
        
        Args: prop_details (List[str]): Easting, northing, primary address, secondary address, town, postcode, MCM code of property to be uploaded
        """
        if utils.is_valid_res(prop_details):
            self.res_eastings.append(float(prop_details[0]))
            self.res_northings.append(float(prop_details[1]))
            self.res_addresses.append(f"{prop_details[2]} {prop_details[3]}")
            self.res_towns.append(prop_details[4])
            self.res_postcodes.append(prop_details[5])
            self.res_mcms.append(int(prop_details[7]))

            self.res_count += 1
            self.res_ground_levels.append(None)

        elif utils.is_valid_non_res(prop_details):
            self.non_res_eastings.append(float(prop_details[0]))
            self.non_res_northings.append(float(prop_details[1]))
            self.non_res_addresses.append(f"{prop_details[2]} {prop_details[3]}")
            self.non_res_towns.append(prop_details[4])
            self.non_res_postcodes.append(prop_details[5])
            self.non_res_floor_areas.append(float(prop_details[6]))
            self.non_res_mcms.append(int(prop_details[7]))

            self.non_res_count += 1
            self.non_res_ground_levels.append(None)

    def add_node(self, node_details: List[str]) -> None:
        """ Add node details (if valid) to data handler

        Args:
            node_details (List[str]): Easting, northing, depths at various return periods
        """
        if utils.is_valid_node(node_details):
            self.node_eastings.append(None if self.is_blank(node_details[0]) else float(node_details[0])) 
            self.node_northings.append(None if self.is_blank(node_details[1]) else float(node_details[1]))


            depths = node_details[2::]
            clean_depths = [None if self.is_blank(
                depth) else float(depth) for depth in depths]

            self.node_depths.append(clean_depths)

            self.node_count += 1

    def add_ascii(self, fname: str) -> None:
        """ Add ASCII grid information to data handler

        Args:
            fname (str): Filename of ASCII grid to be added
        """
        # Get and clean headers
        header = [getline(fname, i+1) for i in range(6)]
        header_clean = [int(re.search(r'-?\d+', datapoint).group())
                        for datapoint in header]

        # Get body
        body = np.loadtxt(fname, skiprows=6)

        # Filter NODATAs
        body = np.where(body == header_clean[-1], None, body)

        # Add to master lists
        self.ascii_fnames.append(fname)

        self.n_rows.append(len(body))
        self.n_cols.append(len(body[0]))

        self.x_corners.append(header_clean[2])
        self.y_corners.append(header_clean[3])
        self.cellsizes.append(header_clean[4])
        self.nodata_values.append(header_clean[5])

        self.raster_points.append(body)

        # Update counts
        self.ascii_count += 1

    def add_props_from_table(self, columns: List[int], table: QTableWidget) -> None:
        """ Add properties found in a QTableWidget to data hander

        Args:
            columns (List[int]): List of columns containing relevant property information
            table (QTableWidget): Table containing property information
        """
        all_props = utils.read_table_with_columns(columns, table)
        for prop in all_props:
            self.add_prop(prop)

    def add_nodes_from_table(self, columns: List[int], table: QTableWidget) -> None:
        """ Add nodes found in a QTableWidget to data handler

        Args:
            columns (List[int]): List of columns containing relevant node information
            table (QTableWidget): Table containing node information
        """
        nodes_found = utils.read_table_with_columns(columns, table)
        for node in nodes_found:
            self.add_node(node)

    def edit_res(self, prop_details: List[str], gl: str, index: int) -> None:
        """ Edit details of residential property found in data handler

        Args:
            prop_details (List[str]): New easting, northing, address, town, postcode, and MCM code values
            gl (str): New ground level value
            index (int): Index of property to be edited
        """
        self.res_eastings[index] = float(prop_details[0])
        self.res_northings[index] = float(prop_details[1])
        self.res_addresses[index] = prop_details[2]
        self.res_towns[index] = prop_details[3]
        self.res_postcodes[index] = prop_details[4]
        self.res_mcms[index] = int(prop_details[5])
        
        self.res_ground_levels[index] = float(gl) if bool(gl and gl.strip()) else None

    def edit_non_res(self, prop_details: List[str], gl: str, index: int) -> None:
        """ Edit details of non-residential property found in data handler

        Args:
            prop_details (List[str]): New easting, northing, address, town, postcode, floor area, and MCM code values
            gl (str): New ground level value
            index (int): Index of property to be edited
        """
        self.non_res_eastings[index] = float(prop_details[0])
        self.non_res_northings[index] = float(prop_details[1])
        self.non_res_addresses[index] = prop_details[2]
        self.non_res_towns[index] = prop_details[3]
        self.non_res_postcodes[index] = prop_details[4]
        self.non_res_floor_areas[index] = float(prop_details[5])
        self.non_res_mcms[index] = int(prop_details[6])

        # Check ground level is not blank        
        self.non_res_ground_levels[index] = float(gl) if bool(gl and gl.strip()) else None

    def edit_node(self, node_details: List[str], index: int) -> None:
        """ Edit details of node found in data handler

        Args:
            node_details (List[str]): New easting, northing, and depths at various return periods values
            index (int): Index of node to be edited 
        """
        self.node_eastings[index] = None if self.is_blank(
            node_details[0]) else float(node_details[0])
        self.node_northings[index] = None if self.is_blank(
            node_details[1]) else float(node_details[1])
        for j in range(len(self.return_periods)):
            self.node_depths[index][j] = None if self.is_blank(
                node_details[j+2]) else float(node_details[j+2])

    def edit_ascii(self, ascii_details: List[str], index: int) -> None:
        """ Edit selected details of ASCII grid found in data handler
        NOTE: Only filename, corner coordinates and cellsizes can be edited

        Args:
            ascii_details (List[str]): New filename, corner x coordinate, corner y coordinate, and cellsize values
            index (int): Index of ASCII grid to be edited
        """     
        self.ascii_fnames[index] = None if self.is_blank(
            ascii_details[0]) else ascii_details[0]
        self.x_corners[index] = None if self.is_blank(
            ascii_details[1]) else int(ascii_details[1])
        self.y_corners[index] = None if self.is_blank(
            ascii_details[2]) else int(ascii_details[2])
        self.cellsizes[index] = None if self.is_blank(
            ascii_details[3]) else int(ascii_details[3])

    def delete_res(self, index: int) -> None:
        """ Remove residential property from data handler

        Args:
            index (int): Index of property to be removed
        """ 
        del self.res_eastings[index]
        del self.res_northings[index]
        del self.res_addresses[index]
        del self.res_towns[index]
        del self.res_postcodes[index]
        del self.res_mcms[index]
        del self.res_ground_levels[index]

        self.res_count -= 1

    def delete_non_res(self, index: int) -> None:
        """ Remove non-residential property from data handler

        Args:
            index (int): Index of property to be removed
        """
        del self.non_res_eastings[index]
        del self.non_res_northings[index]
        del self.non_res_addresses[index]
        del self.non_res_towns[index]
        del self.non_res_postcodes[index]
        del self.non_res_mcms[index]
        del self.non_res_floor_areas[index]
        del self.non_res_ground_levels[index]

        self.non_res_count -= 1

    def delete_node(self, index: int) -> None:
        """ Remove node from data handler

        Args:
            index (int): Index of node to be removed
        """
        del self.node_eastings[index]
        del self.node_northings[index]
        del self.node_depths[index]

        self.node_count -= 1

    def delete_ascii(self, index: int) -> None: 
        """ Remove ASCII grid from data handler
        
        Args:
            index (int): Index of ASCII grid to be removed
        """
        del self.ascii_fnames[index]
        del self.n_cols[index]
        del self.n_rows[index]
        del self.x_corners[index]
        del self.y_corners[index]
        del self.cellsizes[index]
        del self.nodata_values[index]
        del self.raster_points[index]

        self.ascii_count -= 1

    def get_res_elevations(self) -> None:
        """ Calculate ground level of residential properties from ASCII grids
        """
        for i in range(self.res_count):
            x = self.res_eastings[i]
            y = self.res_northings[i]

            for j in range(self.ascii_count):
                x_start = self.x_corners[j]
                x_stop = x_start + (self.n_cols[j] * self.cellsizes[j])
                y_start = self.y_corners[j]
                y_stop = y_start + (self.n_rows[j] * self.cellsizes[j])

                # Res is located in ASCII grid
                if x > x_start and x < x_stop and y > y_start and y < y_stop:

                    # Round x and y to the nearest multiple of ASCII cellsize
                    # This finds the nearest measured point in the grid to (x,y)
                    round_x = int(self.cellsizes[j]
                                  * round(x/self.cellsizes[j]))
                    round_y = int(self.cellsizes[j]
                                  * round(y/self.cellsizes[j]))

                    x_index = int((round_x - x_start) / self.cellsizes[j])
                    y_index = int(
                        self.n_rows[j] - ((round_y - y_start) / self.cellsizes[j]))

                    # Indexes at top edges of ASCII grids need to be rounded down
                    if x_index == self.n_cols[j]:
                        x_index -= 1

                    if y_index == self.n_rows[j]:
                        y_index -= 1

                    self.res_ground_levels[i] = self.raster_points[j][y_index][x_index]

    def get_non_res_elevations(self) -> None:
        """ Calculate ground level of non-residential properties from ASCII grids
        """
        for i in range(self.non_res_count):
            x = self.non_res_eastings[i]
            y = self.non_res_northings[i]

            for j in range(self.ascii_count):
                x_start = self.x_corners[j]
                x_stop = x_start + (self.n_cols[j] * self.cellsizes[j])
                y_start = self.y_corners[j]
                y_stop = y_start + (self.n_rows[j] * self.cellsizes[j])

                # Non res is located in ASCII grid
                if x > x_start and x < x_stop and y > y_start and y < y_stop:

                    # Round x and y to the nearest multiple of ASCII cellsize
                    # This finds the nearest measured point in the grid to (x,y)
                    round_x = int(self.cellsizes[j]
                                  * round(x/self.cellsizes[j]))
                    round_y = int(self.cellsizes[j]
                                  * round(y/self.cellsizes[j]))

                    x_index = int((round_x - x_start) / self.cellsizes[j])
                    y_index = int(
                        self.n_rows[j] - ((round_y - y_start) / self.cellsizes[j]))

                    # Indexes at top edges of ASCII grids need to be rounded own
                    if x_index == self.n_cols[j]:
                        x_index -= 1

                    if y_index == self.n_rows[j]:
                        y_index -= 1

                    self.non_res_ground_levels[i] = self.raster_points[j][y_index][x_index]

    def is_blank(self, s: str) -> bool:
        """
        Test for empty or blank string
        """
        return not (s and s.strip())

    def get_major_datapoints(self) -> None:
        """ Get 2D list of major datapoints to be displayed in summary tables
        """
        return [
            [self.total_average_res_damage, self.total_lifetime_res_damage, self.annual_res_damage_after, self.lifetime_res_damage_after, self.current_annual_res_benefit, self.current_lifetime_res_benefit],
            [self.total_average_intangible_damage, self.total_lifetime_intangible_damage, self.annual_intangible_damage_after, self.lifetime_intangible_damage_after, self.current_annual_intangible_benefit, self.current_lifetime_intangible_benefit],
            [self.total_average_mh_costs, self.total_lifetime_mh_costs, self.annual_mh_damage_after, self.lifetime_mh_damage_after, self.current_annual_mh_benefit, self.current_lifetime_mh_benefit],
            [self.total_average_vehicular_damages, self.total_lifetime_vehicular_damages, self.annual_vehicle_damage_after, self.lifetime_vehicle_damage_after, self.current_annual_vehicle_benefit, self.current_lifetime_vehicle_benefit],
            [self.total_average_evac_costs, self.total_lifetime_evac_costs, self.annual_evac_damage_after, self.lifetime_evac_damage_after, self.current_annual_evac_benefit, self.current_lifetime_evac_benefit],
            [self.total_average_non_res_damage, self.total_lifetime_non_res_damage, self.annual_non_res_damage_after, self.lifetime_non_res_damage_after, self.current_annual_non_res_benefit, self.current_lifetime_non_res_benefit],
            [self.total_average_disruption, self.total_lifetime_disruption, self.annual_disruption_after, self.lifetime_disruption_after, self.current_annual_disruption_benefit, self.current_lifetime_disruption_benefit],
            [self.total_average_infrastructure_damage, self.total_lifetime_infrastructure_damage, self.annual_infrastructure_damage_after, self.lifetime_infrastructure_damage_after, self.current_annual_infrastructure_benefit, self.current_lifetime_infrastructure_benefit],
            [self.total_average_emergency_services_costs, self.total_lifetime_emergency_services_costs, self.annual_emergency_services_cost_after, self.lifetime_emergency_services_cost_after, self.current_annual_emergency_services_benefit, self.current_lifetime_emergency_services_benefit],
            [self.total_average_annual_damage, self.total_lifetime_damage, self.total_annual_damage_after, self.total_lifetime_damage, self.total_current_annual_benefit, self.total_current_lifetime_benefit]
        ]

    """
    DAMAGES METHODS
    """

    def get_damages(self) -> None:
        """ Calculate all damages from currently uploaded info
        """
        # Access flood information
        self.df = utils.get_cumulative_discount_factor(self.scheme_lifetime)
        self.health_df = utils.get_cumulative_health_discount_factor(
            self.scheme_lifetime)

        # Access res information
        self.clean_res_e = utils.apply_checks(
            self.res_checks, self.res_eastings)
        self.clean_res_n = utils.apply_checks(
            self.res_checks, self.res_northings)
        self.clean_res_m = utils.apply_checks(self.res_checks, self.res_mcms)
        self.clean_res_gl = utils.apply_checks(
            self.res_checks, self.res_ground_levels)
        self.clean_res_a = utils.apply_checks(
            self.res_checks, self.res_addresses)

        # Access non-res information
        self.clean_non_res_e = utils.apply_checks(
            self.non_res_checks, self.non_res_eastings)
        self.clean_non_res_n = utils.apply_checks(
            self.non_res_checks, self.non_res_northings)
        self.clean_non_res_m = utils.apply_checks(
            self.non_res_checks, self.non_res_mcms)
        self.clean_non_res_gl = utils.apply_checks(
            self.non_res_checks, self.non_res_ground_levels)
        self.clean_non_res_a = utils.apply_checks(
            self.non_res_checks, self.non_res_addresses)
        self.clean_non_res_fa = utils.apply_checks(
            self.non_res_checks, self.non_res_floor_areas)

        # Access node information
        self.clean_node_e = utils.apply_checks(
            self.node_checks, self.node_eastings)
        self.clean_node_n = utils.apply_checks(
            self.node_checks, self.node_northings)
        self.clean_node_d = utils.apply_checks(
            self.node_checks, self.node_depths)

        # Update damages fields
        self.get_residential_damages()
        self.get_intangible_damages()
        self.get_mental_health_damages()
        self.get_vehicular_damages()
        self.get_evac_damages()
        self.get_non_residential_damages()
        self.get_disruption_damages()
        self.get_infrastructure_damages()
        self.get_emergency_services_damages()
        self.get_total_damages()

    def get_residential_damages(self) -> None:
        """ Calculate damages occuring to residential properties 
        """
        # Access flood information
        event_damages = utils.get_res_event_damages(self.event_type)

        # Get indexes of nearest nodes
        node_indexes = [utils.get_nearest_node(
            self.clean_res_e[i],
            self.clean_res_n[i],
            zip(self.clean_node_e, self.clean_node_n)) for i in range(self.clean_res_count)]

        # Depths at each property during each flood event
        self.res_depths = [[depth - self.clean_res_gl[i]
                            for depth in self.clean_node_d[node_indexes[i]]] for i in range(self.clean_res_count)]

        # Access direct damages per property based on MCM code
        res_direct_damages = [event_damages[self.clean_res_m[i]]
                              for i in range(self.clean_res_count)]

        # Interpolate to find damages
        self.res_damages = [utils.interpolate_res_damages(
            res_direct_damages[i],
            self.res_depths[i]) for i in range(self.clean_res_count)]

        # Apply trapezium rule
        self.average_annual_damage_per_res = [utils.get_average_annual(
            self.return_periods, self.res_damages[i]) for i in range(self.clean_res_count)]

        # Apply cumulative discount factor
        self.lifetime_damage_per_res = [
            (damage * self.df) for damage in self.average_annual_damage_per_res]

        # Sums
        self.total_average_res_damage = sum(self.average_annual_damage_per_res)
        self.total_lifetime_res_damage = sum(self.lifetime_damage_per_res)

        # Capped depths set equal to uncapped depths
        # Then written over if capping is enabled
        self.capped_res_depths = self.res_depths.copy()

        # Capped damages set equal to uncapped damages
        # Then written over if capping is enabled
        self.capped_res_damages = self.res_damages.copy()

        if self.caps_enabled:
            # Compare lifetime damages and user-entered cap
            self.capped_lifetime_damage_per_res = [
                min(self.res_cap, self.lifetime_damage_per_res[i]) for i in range(self.clean_res_count)]

            self.capped_average_annual_damage_per_res = [
                (damage/self.df) for damage in self.capped_lifetime_damage_per_res]

            # Update sums
            self.total_average_res_damage = sum(
                self.capped_average_annual_damage_per_res)
            self.total_lifetime_res_damage = sum(
                self.capped_lifetime_damage_per_res)

            # Find capping depths for each property
            # Cap all depths higher than it
            for prop in range(self.clean_res_count):
                cap = utils.get_capping_depth(
                    self.return_periods,
                    self.res_depths[prop],
                    self.res_damages[prop],
                    self.res_cap,
                    self.df)

                # Update capped depths and damages
                depths = self.res_depths[prop]
                damages = self.res_damages[prop]
                if cap is not None:
                    self.capped_res_depths[prop] = [
                        min(depth, cap) for depth in depths]
                    self.capped_res_damages[prop] = [min(
                        damage, self.capped_average_annual_damage_per_res[prop]) for damage in damages]

    def get_intangible_damages(self) -> None:
        """ Calculate intangible damages arising from flood event
        """
        self.current_sops = [utils.get_current_sop(
            self.return_periods, self.capped_res_depths[i]) for i in range(self.clean_res_count)]

        # Interpolate to find average annual
        self.average_annual_intangible_damages = [
            utils.get_intangible_damage(sop) for sop in self.current_sops]

        # Apply cumulative health discount factor
        self.lifetime_intangible_damages = [
            (damage * self.health_df) for damage in self.average_annual_intangible_damages]

        # Sums
        self.total_average_intangible_damage = sum(
            self.average_annual_intangible_damages)
        self.total_lifetime_intangible_damage = sum(
            self.lifetime_intangible_damages)

    def get_mental_health_damages(self) -> None:
        """ Calculate mental health costs arising from flood event
        """
        self.mh_costs = [utils.get_mh_costs(
            self.capped_res_depths[i], self.clean_res_m[i]) for i in range(self.clean_res_count)]

        # Apply trapezium rule
        self.average_annual_mh_costs = [utils.get_average_annual(
            self.return_periods, self.mh_costs[i]) for i in range(self.clean_res_count)]

        # Apply cumulative discount factor
        self.lifetime_mh_costs = [(damage * self.health_df)
                                  for damage in self.average_annual_mh_costs]

        # Sums
        self.total_average_mh_costs = sum(self.average_annual_mh_costs)
        self.total_lifetime_mh_costs = sum(self.lifetime_mh_costs)

    def get_vehicular_damages(self) -> None:
        """ Calcuate vehicular damages arising from flood event
        """
        # Find weighting from event type
        weighting = 0.75
        if self.event_type in [
            "Short Duration Major Flood Storm No Warning",
            "Long Duration Major Flood Storm No Warning",
                "Extra-Long Duration Major Flood Storm No Warning"]:
            weighting = 1

        # utils functions adjusts for internal property threshold
        # 0.15m addition is NOT required
        self.vehicular_damages = [utils.get_vehicle_damages(
            depths, weighting) for depths in self.capped_res_depths]

        # Apply trapezium rule
        self.average_annual_vehicular_damages = [utils.get_average_annual(
            self.return_periods, self.vehicular_damages[i]) for i in range(self.clean_res_count)]

        # Apply cumulative discount factor
        self.lifetime_vehicular_damages = [
            (damage * self.df) for damage in self.average_annual_vehicular_damages]

        # Sums
        self.total_average_vehicular_damages = sum(
            self.average_annual_vehicular_damages)
        self.total_lifetime_vehicular_damages = sum(
            self.lifetime_vehicular_damages)

    def get_evac_damages(self) -> None:
        """ Calculate evacuation costs arising from flood event
        """
        # Get direct evac costs based on event type
        direct_costs = utils.get_evac_category_costs(self.evac_cost_category)

        res_direct_costs = [direct_costs[mcm] for mcm in self.clean_res_m]

        # Interpolate to find damages
        self.evac_costs = [utils.get_evac_costs(
            res_direct_costs[i], self.capped_res_depths[i]) for i in range(self.clean_res_count)]

        # Apply trapezium rule
        self.average_annual_evac_costs = [utils.get_average_annual(
            self.return_periods, self.evac_costs[i]) for i in range(self.clean_res_count)]

        # Applt cumulative discount factor
        self.lifetime_evac_costs = [(damage * self.df)
                                    for damage in self.average_annual_evac_costs]

        # Sums
        self.total_average_evac_costs = sum(self.average_annual_evac_costs)
        self.total_lifetime_evac_costs = sum(self.lifetime_evac_costs)

    def get_non_residential_damages(self) -> None:
        """ Calculate damages occuring to non-residential properties
        """
        # Access flood information
        event_damages = utils.get_non_res_event_damages(
            self.event_type, self.cellar)

        # Get indexes of nearest nodes
        node_indexes = [utils.get_nearest_node(
            self.clean_non_res_e[i],
            self.clean_non_res_n[i],
            zip(self.clean_node_e, self.clean_node_n)) for i in range(self.clean_non_res_count)]

        # Depths at each property during each flood event
        self.non_res_depths = [[depth - self.clean_non_res_gl[i]
                                for depth in self.clean_node_d[node_indexes[i]]] for i in range(self.clean_non_res_count)]

        # Access direct damages per property based on MCM code
        non_res_direct_damages = [
            event_damages[self.clean_non_res_m[i]] for i in range(self.clean_non_res_count)]

        # Interpolate to find damages
        non_res_damages_per_metre = [utils.interpolate_non_res_damages(
            non_res_direct_damages[i],
            self.non_res_depths[i]) for i in range(self.clean_non_res_count)]

        # Multiply damages by area of each property
        self.non_res_damages = [[damage * self.clean_non_res_fa[i]
                                 for damage in non_res_damages_per_metre[i]] for i in range(self.clean_non_res_count)]

        # Apply trapezium rule
        self.average_annual_damage_per_non_res = [utils.get_average_annual(
            self.return_periods, self.non_res_damages[i]) for i in range(self.clean_non_res_count)]

        # Apply cumulative discount factor
        self.lifetime_damage_per_non_res = [
            (damage * self.df) for damage in self.average_annual_damage_per_non_res]

        # Sums
        self.total_average_non_res_damage = sum(
            self.average_annual_damage_per_non_res)
        self.total_lifetime_non_res_damage = sum(
            self.lifetime_damage_per_non_res)

        # Capped depths set equal to uncapped depths
        # Then written over if capping is enabled
        self.capped_non_res_depths = self.non_res_depths.copy()

        # Capped damages set equal to uncapped damages
        # Then written over if capping is enabled

        if self.caps_enabled:
            # Compare lifetime damages and user-entered cap
            self.capped_lifetime_damage_per_non_res = [min(
                self.non_res_cap, self.lifetime_damage_per_non_res[i]) for i in range(self.clean_non_res_count)]

            self.capped_average_annual_damage_per_non_res = [
                (damage/self.df) for damage in self.capped_lifetime_damage_per_non_res]

            # Update sums
            self.total_average_non_res_damage = sum(
                self.capped_average_annual_damage_per_non_res)
            self.total_lifetime_non_res_damage = sum(
                self.capped_lifetime_damage_per_non_res)

            # Find capping depths for each property
            # Cap all depths higher than it
            for prop in range(self.clean_non_res_count):
                cap = utils.get_capping_depth(
                    self.return_periods,
                    self.non_res_depths[prop],
                    self.non_res_damages[prop],
                    self.non_res_cap,
                    self.df)

                depths = self.non_res_depths[prop]
                damages = self.non_res_damages[prop]
                if cap is not None:
                    self.capped_non_res_depths[prop] = [
                        min(depth, cap) for depth in depths]
                    self.capped_non_res_damages = [min(
                        damage, self.capped_average_annual_damage_per_non_res[prop]) for damage in damages]

    def get_disruption_damages(self) -> None:
        """ Calculate business disruption damages arising from flood event 
        """
        self.total_average_disruption = self.total_average_non_res_damage * 0.03
        self.total_lifetime_disruption = self.total_lifetime_non_res_damage * 0.03

    def get_infrastructure_damages(self) -> None:
        """ Calculate infrastructure damages from a given flood event
        """
        if self.caps_enabled:
            self.total_average_infrastructure_damage = (
                1/10) * (self.total_average_res_damage + self.total_average_non_res_damage)
            self.total_lifetime_infrastructure_damage = self.total_average_infrastructure_damage * self.df

    def get_emergency_services_damages(self) -> None:
        """ Calculate emergency services and recovery costs arising from a given flood event
        """
        location_weight = utils.get_location_weight(self.location)
        all_damages = [
            self.total_average_res_damage,
            self.total_average_intangible_damage,
            self.total_average_mh_costs,
            self.total_average_vehicular_damages,
            self.total_average_evac_costs,
            self.total_average_non_res_damage,
            self.total_average_disruption
        ]

        self.total_average_emergency_services_costs = sum(
            all_damages) * (location_weight - 1)
        self.total_lifetime_emergency_services_costs = self.total_average_emergency_services_costs * self.health_df

    def get_total_damages(self) -> None:
        """ Calculate total damages arising from a given flood event
        """
        average_damages = [
            self.total_average_res_damage,
            self.total_average_intangible_damage,
            self.total_average_mh_costs,
            self.total_average_vehicular_damages,
            self.total_average_evac_costs,
            self.total_average_non_res_damage,
            self.total_average_disruption,
            self.total_average_infrastructure_damage,
            self.total_average_emergency_services_costs,
        ]

        lifetime_damages = [
            self.total_lifetime_res_damage,
            self.total_lifetime_intangible_damage,
            self.total_lifetime_mh_costs,
            self.total_lifetime_vehicular_damages,
            self.total_lifetime_evac_costs,
            self.total_lifetime_non_res_damage,
            self.total_lifetime_disruption,
            self.total_lifetime_infrastructure_damage,
            self.total_lifetime_emergency_services_costs
        ]

        self.total_average_annual_damage = sum(average_damages)
        self.total_lifetime_damage = sum(lifetime_damages)

    """
    BENEFITS METHODS
    """

    def get_benefits(self) -> None:
        """ Calculate all benefits from currently uploaded info
        """
        self.get_residential_benefits()
        self.get_intangible_benefits()
        self.get_mental_health_benefits()
        self.get_vehicular_benefits()
        self.get_evac_benefits()
        self.get_non_residential_benefits()
        self.get_disruption_benefits()
        self.get_infrastructure_benefits()
        self.get_emergency_services_benefits()
        self.get_total_benefits()

    def get_residential_benefits(self) -> None:
        """ Calculate benefits to residential properties
        """
        # Apply trapezium rule
        self.res_benefits = [utils.get_benefits(
            self.return_periods, self.res_damages[i]) for i in range(self.clean_res_count)]

        # Compare with cap if needed
        if self.caps_enabled:
            self.res_benefits = [[min(self.capped_average_annual_damage_per_res[i], self.res_benefits[i][j]) for j in range(
                len(self.return_periods) - 1)] for i in range(self.clean_res_count)]

        # Sum
        self.total_res_benefits = [sum([self.res_benefits[i][j] for i in range(
            self.clean_res_count)]) for j in range(len(self.return_periods)-1)]

        # Find current benefit
        self.current_annual_res_benefit = utils.get_current_benefit(
            self.return_periods[1::], self.total_res_benefits, self.sop)

        # Apply cumulative discount factor
        self.current_lifetime_res_benefit = self.current_annual_res_benefit * self.df

        # Calculate post-intervention damages
        self.annual_res_damage_after = self.total_average_res_damage - \
            self.current_annual_res_benefit
        self.lifetime_res_damage_after = self.total_lifetime_res_damage - \
            self.current_lifetime_res_benefit

    def get_intangible_benefits(self) -> None:
        """ Calculate intangible benefits
        """
        # Bilinear interpolation
        self.annual_intangible_benefits = [utils.get_intangible_benefit(
            aep, 100/self.sop) for aep in self.current_sops]

        # Apply cumulative discount factor
        self.lifetime_intangible_benefits = [
            (benefit*self.health_df) for benefit in self.annual_intangible_benefits]

        # Totals
        self.current_annual_intangible_benefit = sum(
            self.annual_intangible_benefits)
        self.current_lifetime_intangible_benefit = sum(
            self.lifetime_intangible_benefits)

        # Calculate post-intervention damages
        self.annual_intangible_damage_after = self.total_average_intangible_damage - \
            self.current_annual_intangible_benefit
        self.lifetime_intangible_damage_after = self.total_lifetime_intangible_damage - \
            self.current_lifetime_intangible_benefit

    def get_mental_health_benefits(self) -> None:
        """ Calculate mental health benefits
        """
        # Apply trapezium rule
        self.mh_benefits = [utils.get_benefits(
            self.return_periods, self.mh_costs[i]) for i in range(self.clean_res_count)]

        # Sum
        self.total_mh_benefits = [sum([self.mh_benefits[i][j] for i in range(
            self.clean_res_count)]) for j in range(len(self.return_periods)-1)]

        # Find current benefit
        self.current_annual_mh_benefit = utils.get_current_benefit(
            self.return_periods[1::], self.total_mh_benefits, self.sop)

        # Apply cumulative discount factor
        self.current_lifetime_mh_benefit = self.current_annual_mh_benefit * self.health_df

        # Calculate post-intervention damages
        self.annual_mh_damage_after = self.total_average_mh_costs - \
            self.current_annual_mh_benefit
        self.lifetime_mh_damage_after = self.total_lifetime_mh_costs - \
            self.current_lifetime_mh_benefit

    def get_vehicular_benefits(self) -> None:
        """ Calculate vehicle benefits 
        """
        # Apply trapezium rule
        self.vehicular_benefits = [utils.get_benefits(
            self.return_periods, self.vehicular_damages[i]) for i in range(self.clean_res_count)]

        # Sum
        self.total_vehicular_benefits = [sum([self.vehicular_benefits[i][j] for i in range(
            self.clean_res_count)]) for j in range(len(self.return_periods)-1)]

        # Find current benefit
        self.current_annual_vehicle_benefit = utils.get_current_benefit(
            self.return_periods[1::], self.total_vehicular_benefits, self.sop)

        # Apply cumulative discount factor
        self.current_lifetime_vehicle_benefit = self.current_annual_vehicle_benefit * self.df

        # Calculate post-intervention damages
        self.annual_vehicle_damage_after = self.total_average_vehicular_damages - \
            self.current_annual_vehicle_benefit
        self.lifetime_vehicle_damage_after = self.total_lifetime_vehicular_damages - \
            self.current_lifetime_vehicle_benefit

    def get_evac_benefits(self) -> None:
        """ Calculate evacuation benefits
        """
        # Apply trapezium rule
        self.evac_benefits = [utils.get_benefits(
            self.return_periods, self.evac_costs[i]) for i in range(self.clean_res_count)]

        # Sum
        self.total_evac_benefits = [sum([self.evac_benefits[i][j] for i in range(
            self.clean_res_count)]) for j in range(len(self.return_periods)-1)]

        # Find current benefit
        self.current_annual_evac_benefit = utils.get_current_benefit(
            self.return_periods[1::], self.total_evac_benefits, self.sop)

        # Apply cumulative discount factor
        self.current_lifetime_evac_benefit = self.current_annual_evac_benefit * self.df

        # Calculate post-intervention damages
        self.annual_evac_damage_after = self.total_average_evac_costs - \
            self.current_annual_evac_benefit
        self.lifetime_evac_damage_after = self.total_lifetime_evac_costs - \
            self.current_lifetime_evac_benefit

    def get_non_residential_benefits(self) -> None:
        """ Calculate benefits to non-residential properties
        """
        # Apply trapezium rule
        self.non_res_benefits = [utils.get_benefits(
            self.return_periods, self.non_res_damages[i]) for i in range(self.clean_non_res_count)]

        # Compare with caps if needed
        if self.caps_enabled:
            self.non_res_benefits = [[min(self.capped_average_annual_damage_per_non_res[i], self.non_res_benefits[i][j]) for j in range(
                len(self.return_periods) - 1)] for i in range(self.clean_non_res_count)]

        # Sum
        self.total_non_res_benefits = [sum([self.non_res_benefits[i][j] for i in range(
            self.clean_non_res_count)]) for j in range(len(self.return_periods)-1)]

        # Find current benefit
        self.current_annual_non_res_benefit = utils.get_current_benefit(
            self.return_periods[1::], self.total_non_res_benefits, self.sop)

        # Apply cumulative discount factor
        self.current_lifetime_non_res_benefit = self.current_annual_non_res_benefit * self.df

        # Calculate post-intervention damages
        self.annual_non_res_damage_after = self.total_average_non_res_damage - \
            self.current_annual_non_res_benefit
        self.lifetime_non_res_damage_after = self.total_lifetime_non_res_damage - \
            self.current_lifetime_non_res_benefit

    def get_disruption_benefits(self) -> None:
        """ Calculate relative benefits to business disruption
        """
        # Benefits
        self.current_annual_disruption_benefit = self.current_annual_non_res_benefit * 0.03
        self.current_lifetime_disruption_benefit = self.current_lifetime_non_res_benefit * 0.03

        # Post-intervention damages
        self.annual_disruption_after = self.annual_non_res_damage_after * 0.03
        self.lifetime_disruption_after = self.lifetime_disruption_after * 0.03

    def get_infrastructure_benefits(self) -> None:
        """ Calculate infrastructure benefits
        """

        # Calculate post-intervention damages
        self.annual_infrastructure_damage_after = (
            self.annual_res_damage_after + self.annual_non_res_damage_after) * 0.1
        self.lifetime_infrastructure_damage_after = self.annual_infrastructure_damage_after * self.df

        # Calculate benefits
        self.current_annual_infrastructure_benefit = self.total_average_infrastructure_damage - \
            self.annual_infrastructure_damage_after
        self.current_lifetime_infrastructure_benefit = self.current_annual_infrastructure_benefit * self.df

    def get_emergency_services_benefits(self) -> None:
        """ Calculate emergency services and recovery benefits arising from given flood event
        """
        location_weight = utils.get_location_weight(self.location)
        all_damages = [
            self.annual_res_damage_after,
            self.annual_intangible_damage_after,
            self.annual_mh_damage_after,
            self.annual_vehicle_damage_after,
            self.annual_evac_damage_after,
            self.annual_non_res_damage_after,
            self.annual_disruption_after
        ]

        # Post-intervention damages
        self.annual_emergency_services_cost_after = sum(
            all_damages) * (location_weight - 1)
        self.lifetime_emergency_services_cost_after = self.annual_emergency_services_cost_after * self.health_df

        # Benefits
        self.current_annual_emergency_services_benefit = self.total_average_emergency_services_costs - \
            self.annual_emergency_services_cost_after
        self.current_lifetime_emergency_services_benefit = self.current_annual_emergency_services_benefit * self.health_df

    def get_total_benefits(self) -> None:
        """ Calculate total benefits arising from flood event
        """
        # Post-intervention damages
        annual_post_damages = [
            self.annual_res_damage_after,
            self.annual_intangible_damage_after,
            self.annual_mh_damage_after,
            self.annual_vehicle_damage_after,
            self.annual_evac_damage_after,
            self.annual_non_res_damage_after,
            self.annual_disruption_after,
            self.annual_infrastructure_damage_after,
            self.annual_emergency_services_cost_after
        ]
        self.total_annual_damage_after = sum(annual_post_damages)

        lifetime_post_damages = [
            self.lifetime_res_damage_after,
            self.lifetime_intangible_damage_after,
            self.lifetime_mh_damage_after,
            self.lifetime_vehicle_damage_after,
            self.lifetime_evac_damage_after,
            self.lifetime_non_res_damage_after,
            self.lifetime_disruption_after,
            self.lifetime_infrastructure_damage_after,
            self.lifetime_emergency_services_cost_after
        ]
        self.total_lifetime_damage_after = sum(lifetime_post_damages)

        # Benefits
        annual_benefits = [
            self.current_annual_res_benefit,
            self.current_annual_intangible_benefit,
            self.current_annual_mh_benefit,
            self.current_annual_vehicle_benefit,
            self.current_annual_evac_benefit,
            self.current_annual_non_res_benefit,
            self.current_annual_disruption_benefit,
            self.current_annual_infrastructure_benefit,
            self.current_annual_emergency_services_benefit
        ]
        self.total_current_annual_benefit = sum(annual_benefits)

        lifetime_benefits = [
            self.current_lifetime_res_benefit,
            self.current_lifetime_intangible_benefit,
            self.current_lifetime_mh_benefit,
            self.current_lifetime_vehicle_benefit,
            self.current_lifetime_evac_benefit,
            self.current_lifetime_non_res_benefit,
            self.current_lifetime_disruption_benefit,
            self.current_lifetime_infrastructure_benefit,
            self.current_lifetime_emergency_services_benefit
        ]
        self.total_current_lifetime_benefit = sum(lifetime_benefits)

    """
    RESULTS EXPORTING
    """

    def export_results(self, fname: str, damages: List[bool], benefits: List[bool], file_formats: List[bool]) -> None:
        """ Write selected appraisal results in selected formats

        Args:
            fname (str): Location of results folders
            damages (List[bool]): Damage results to be saved
            benefits (List[bool]): Benefit results to be saved
            file_formats (List[bool]): File formats for results to be written in
        """
        # Build directories
        self.build_folders(fname, file_formats)

        # Write summary
        self.write_summary(fname, file_formats)

        damages_funcs = [
            self.write_res_damages,
            self.write_intangible_damages,
            self.write_mh_damages,
            self.write_vehicle_damages,
            self.write_evac_damages,
            self.write_non_res_damages
        ]
        # Execute selected damage functions
        for i in range(len(damages)):
            if damages[i]:
                damages_funcs[i](fname, file_formats)

        benefits_funcs = [
            self.write_res_benefits,
            self.write_intangible_benefits,
            self.write_mh_benfits,
            self.write_vehicle_benefits,
            self.write_evac_benefits,
            self.write_non_res_benefits
        ]
        # Execute selected benefit functions
        for i in range(len(benefits)):
            if benefits[i]:
                benefits_funcs[i](fname, file_formats)

    def build_folders(self, fname: str, file_formats: List[bool]) -> None:
        """ Write folders for results to be saved in

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        csv_path = os.path.join(fname, "CSVs")
        xlsx_path = os.path.join(fname, "XLSXs")

        # Make parent folder if it doesnt exist
        if not os.path.exists(fname):
            os.mkdir(fname)

        # CSV format selected
        if file_formats[0]:
            if not os.path.exists(csv_path):
                os.mkdir(csv_path)

        # XLSX format selected
        if file_formats[1]:
            if not os.path.exists(xlsx_path):
                os.mkdir(xlsx_path)

    def write_summary(self, fname: str, file_formats: List[bool]) -> None:
        """ Write summary results

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results in be written in
        """
        # Table headings
        dataset = [["Damage Type", "Existing Annual Damage (£)", "Existing Lifetime Damage (£)", "Post-intervention Annual Damage (£)",
                    "Post-intervention Lifetime Damage (£)", "Annual Benefits (£)", "Lifetime Benefits (£)"]]
        row_headers = [
            "Residential",
            "Intangible",
            "Mental Health",
            "Vehicular",
            "Evacuation",
            "Non-Residential",
            "Business Disruption",
            "Infrastructure",
            "Emergeny Services and Recovery",
            "Total"
        ]

        # Main data
        main_data = self.get_major_datapoints()
        for i in range(len(row_headers)):
            row = [row_headers[i]] + main_data[i]
            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Results Summary.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Results Summary.xlsx"))

    def write_res_damages(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of residential damages

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [
            ["Address", "Average Annual Damage (£)", "Lifetime Damage (£)"]]
        if self.caps_enabled:
            # Add cap-related headings
            dataset[0] += [
                "Capped Average Annual Damage (£)", "Capped Lifetime Damage (£)"]
        dataset[0] += [f"{round(100/rp, 2)}% AEP Damage (£)" for rp in self.return_periods]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i], self.average_annual_damage_per_res[i],
                   self.lifetime_damage_per_res[i]]
            if self.caps_enabled:
                # Add cap-related data if required
                row += [self.capped_average_annual_damage_per_res[i],
                        self.capped_lifetime_damage_per_res[i]]
            row += self.res_damages[i]

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Residential Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Residential Damages.xlsx"))

    def write_intangible_damages(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of intangible damages

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        dataset = [
            ["Address", "Current SOP (AEP %)", "Average Annual Damage (£)", "Lifetime Damage (£)"]]
        for i in range(self.clean_res_count):
            dataset.append([self.clean_res_a[i], self.current_sops[i],
                           self.average_annual_intangible_damages[i], self.lifetime_intangible_damages[i]])

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Intangible Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Intangible Damages.xlsx"))

    def write_mh_damages(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of mental health damages

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [["Address", "Average Annual Damage (£)", "Lifetime Damage (£)"] + [f"{round(100/rp, 2)}% AEP Damage (£)" for rp in self.return_periods]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i], self.average_annual_mh_costs[i],
                   self.lifetime_mh_costs[i]]
            row += self.mh_costs[i]

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Mental Health Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Mental Health Damages.xlsx"))

    def write_vehicle_damages(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of vehicular damages

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in 
        """
        # Table headings
        dataset = [["Address", "Average Annual Damage", "Lifetime Damage (£)"] + [f"{round(100/rp, 2)}% AEP Damage (£)" for rp in self.return_periods]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i], self.average_annual_vehicular_damages[i],
                   self.lifetime_vehicular_damages[i]]
            row += self.vehicular_damages[i]

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Vehicle Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Vehicle Damages.xlsx"))

    def write_evac_damages(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing evacuation damages

        Args:
            fname (str): Location of results folders           
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [["Address", "Average Annual Damage (£)", "Lifetime Damage (£)"] + [f"{round(100/rp, 2)}% AEP Damage (£)" for rp in self.return_periods]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i], self.average_annual_evac_costs[i],
                   self.lifetime_evac_costs[i]]
            row += self.evac_costs[i]

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Evacuation Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Evacuation Damages.xlsx"))

    def write_non_res_damages(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of non-residential damages

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [
            ["Address", "Average Annual Damage (£)", "Lifetime Damage (£)"]]
        if self.caps_enabled:
            # Add cap-related headings
            dataset[0] += [
                "Capped Average Annual Damage (£)", "Capped Lifetime Damage (£)"]
        dataset[0] += [f"{round(100/rp, 2)}% AEP Damage (£)"for rp in self.return_periods]

        # Main data
        for i in range(self.clean_non_res_count):
            row = [self.clean_non_res_a[i], self.average_annual_damage_per_non_res[i],
                   self.lifetime_damage_per_non_res[i]]
            if self.caps_enabled:
                # Add cap-related data if required
                row += [self.capped_average_annual_damage_per_non_res[i],
                        self.capped_lifetime_damage_per_non_res[i]]
            row += self.non_res_damages[i]

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Non-Residential Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Non-Residential Damages.xlsx"))

    def write_res_benefits(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of residential benefits

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [["Address"] + [f"{round(100/rp, 2)}% AEP Benefit (£)" for rp in self.return_periods[1::]]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i]] + self.res_benefits[i]
            dataset.append(row)

        # Totals
        totals = ["Total Residential Benefit"] + self.total_res_benefits
        dataset.append(totals)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Residential Benefits.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Residential Benefits.xlsx"))

    def write_intangible_benefits(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of intangible benefits

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [
            ["Address", "Average Annual Benefit (£)", "Lifetime Benefit (£)"]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i], self.annual_intangible_benefits[i],
                   self.lifetime_intangible_damages[i]]
            dataset.append(row)

        # Totals
        totals = ["Total Intangible Benefit", self.current_annual_intangible_benefit,
                  self.current_lifetime_intangible_benefit]
        dataset.append(totals)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Intangible Benefits.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Intangible Benefits.xlsx"))

    def write_mh_benfits(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of mental health benefits

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [["Address"] + [f"{round(100/rp, 2)}% AEP Benefit (£)" for rp in self.return_periods[1::]]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i]] + self.mh_benefits[i]
            dataset.append(row)

        # Totals
        totals = ["Total Mental Health Benefit"] + self.total_mh_benefits
        dataset.append(totals)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Mental Health Benefits.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Mental Health Benefits.xlsx"))

    def write_vehicle_benefits(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of vehicular benefits

        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """ 
        # Table headings
        dataset = [["Address"] + [f"{round(100/rp, 2)}% AEP Benefit (£)" for rp in self.return_periods[1::]]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i]] + self.mh_benefits[i]
            dataset.append(row)

        # Totals
        totals = ["Total Vehicle Benefit"] + self.total_vehicular_benefits
        dataset.append(totals)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Vehicle Benefits.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Vehicle Benefits.xlsx"))

    def write_evac_benefits(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of evacuation benefits

        Args:
            fname (str): Location of results folders    
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [["Address"] + [f"{round(100/rp, 2)}% AEP Benefit (£)" for rp in self.return_periods[1::]]]

        # Main data
        for i in range(self.clean_res_count):
            row = [self.clean_res_a[i]] + self.evac_benefits[i]
            dataset.append(row)

        # Totals
        totals = ["Total Evacuation Benefit"] + self.total_evac_benefits
        dataset.append(totals)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Evacuation Benefits.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Evacuation Benefits.xlsx"))

    def write_non_res_benefits(self, fname: str, file_formats: List[bool]) -> None:
        """ Write files containing breakdown of non-residential benefits 
        
        Args:
            fname (str): Location of results folders
            file_formats (List[bool]): File formats for results to be written in
        """
        # Table headings
        dataset = [["Address"] + [f"{round(100/rp, 2)}% AEP Benefit (£)" for rp in self.return_periods[1::]]]

        # Main data
        for i in range(self.clean_non_res_count):
            row = [self.clean_non_res_a[i]] + self.non_res_benefits[i]
            dataset.append(row)

        # Totals
        totals = ["Total Non-Residential Benefit"] + \
            self.total_non_res_benefits
        dataset.append(totals)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Non-Residential Benefit.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Non-Residential Benefit.xlsx"))

    """
    SAVING / OPENING
    """

    def save(self, fname: str) -> None:
        """ Write currently loaded appraisal to .Stix file

        Args:
            fname (str): Filename of file to be written
        """
        with open(f"{fname}.Stix", "w") as f:
            json.dump(self.__dict__, f, cls=utils.NumpyEncoder)