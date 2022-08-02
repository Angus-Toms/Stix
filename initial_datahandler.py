"""
Data handling class for initial appraisals performed by Triton FAS

Angus Toms
14 06 2021
"""
import os
from typing import List
 
import const
import utils

class InitialDataHandler():
    def __init__(self) -> None:
        # General flood information
        self.prop_count = 1
        self.warning = "No Warning"
        self.scheme_lifetime = 50
        self.location = "Urban"
        self.sop = 50

        self.df = 0
        self.health_df = 0
        self.direct_damages = []
        self.location_weight = 0

        # Existing Damages
        self.props_at_risk = [0, 0, 0, 0, 0, 0]
        self.cumulative_props_at_risk = [0, 0, 0, 0, 0, 0]
        self.lower_prop_damages = [0, 0, 0, 0, 0, 0]
        self.upper_prop_damages = [0, 0, 0, 0, 0, 0]
        self.lower_emergency_services_cost = 0
        self.upper_emergency_services_cost = 0
        self.lower_annual_damage = 0
        self.upper_annual_damage = 0
        self.lower_lifetime_damage = 0
        self.upper_lifetime_damage = 0

        # Post-intervention damages
        self.props_at_risk_after = [0, 0, 0, 0, 0, 0]
        self.lower_prop_damages_after = [0, 0, 0, 0, 0, 0]
        self.upper_prop_damages_after = [0, 0, 0, 0, 0, 0]
        self.lower_emergency_services_cost_after = 0
        self.upper_emergency_services_cost_after = 0
        self.lower_annual_damage_after = 0
        self.upper_annual_damage_after = 0
        self.lower_lifetime_damage_after = 0
        self.upper_lifetime_damage_after = 0

        # Benefits
        self.lower_benefit = 0
        self.upper_benefit = 0

    """
    GENERAL METHODS
    """

    def get_pre_existing_datapoints(self) -> None:
        """
        Get 2d list of datapoints for pre-exisitng damages to be displayed in results breakdown
        """
        dataset_1 = [[self.props_at_risk[i], self.lower_prop_damages[i],
                      self.upper_prop_damages[i]] for i in range(6)]

        dataset_2 = [
            ["Annual Emergency Services Costs (£)", self.lower_emergency_services_cost,
             self.upper_emergency_services_cost],
            ["Total Average Annual Damage (£)", self.lower_annual_damage,
             self.upper_annual_damage],
            ["Max Lifetime Damage (£)", self.lower_lifetime_damage,
             self.upper_lifetime_damage]
        ]

        return dataset_1 + dataset_2

    def get_major_datapoints(self) -> None:
        """
        Get 2d list of major datapoints to be displayed in summary tables
        """
        dataset_1 = [[self.props_at_risk_after[i], self.lower_prop_damages_after[i],
                      self.upper_prop_damages_after[i]] for i in range(6)]

        dataset_2 = [
            ["Annual Emergency Services Costs After (£)", self.lower_emergency_services_cost_after,
             self.upper_emergency_services_cost_after],
            ["Average Annual Damage After (£)", self.lower_annual_damage_after,
             self.upper_annual_damage_after],
            ["Max Lifetime Damage After (£)", self.lower_lifetime_damage_after,
             self.upper_lifetime_damage_after],
            ["Lifetime Benefit After (£)",
             self.lower_benefit, self.upper_benefit]
        ]

        return dataset_1 + dataset_2

    """
    RESULTS METHODS
    """

    def get_results(self) -> None:
        """
        Call results-calculating methods
        """
        # Update damage fields
        self.get_existing_damages()

        # Update benefit fields
        self.get_benefits()

    def get_existing_damages(self) -> None:
        """
        Calculate existing damages arising from flood events
        """
        # Get general flood info
        self.direct_damages = utils.get_damage_per_prop(self.warning)
        self.location_weight = utils.get_location_weight(self.location)
        self.df = utils.get_cumulative_discount_factor(self.scheme_lifetime)
        self.health_df = utils.get_cumulative_health_discount_factor(
            self.scheme_lifetime)

        # Get property counts
        self.cumulative_props_at_risk = [
            self.prop_count * (i/93) for i in const.props_affected]
        self.props_at_risk = [self.cumulative_props_at_risk[0]] + [
            self.cumulative_props_at_risk[i] - self.cumulative_props_at_risk[i-1] for i in range(1, 6)]

        # Damages
        self.lower_prop_damages = [self.props_at_risk[i]
                                   * self.direct_damages[i+2] for i in range(6)]
        self.upper_prop_damages = [self.props_at_risk[i]
                                   * self.direct_damages[i+1] for i in range(6)]
        self.lower_emergency_services_cost = sum(
            self.lower_prop_damages) * (self.location_weight-1)
        self.upper_emergency_services_cost = sum(
            self.upper_prop_damages) * (self.location_weight-1)
        self.lower_annual_damage = sum(
            self.lower_prop_damages) + self.lower_emergency_services_cost
        self.upper_annual_damage = sum(
            self.upper_prop_damages) + self.upper_emergency_services_cost

        # Apply cumulative discount factors
        self.lower_lifetime_damage = (sum(self.lower_prop_damages) * self.df) + (
            self.lower_emergency_services_cost * self.health_df)
        self.upper_lifetime_damage = (sum(self.upper_prop_damages) * self.df) + (
            self.upper_emergency_services_cost * self.health_df)

    def get_benefits(self) -> None:
        """
        Calculate benefits arising from flood intervention
        """
        # Get property counts
        self.props_at_risk_after = self.props_at_risk.copy()
        if self.sop == 200:
            self.props_at_risk_after = [0, 0, 0, 0, 0, 0]
        else:
            for i in range(6):
                if const.initial_return_periods[i] <= self.sop:
                    self.props_at_risk_after[i +
                                             1] += self.props_at_risk_after[i]
                    self.props_at_risk_after[i] = 0

        # Get damages
        self.lower_prop_damages_after = [
            self.props_at_risk_after[i]*self.direct_damages[i+2] for i in range(6)]
        self.upper_prop_damages_after = [
            self.props_at_risk_after[i]*self.direct_damages[i+1] for i in range(6)]
        self.lower_emergency_services_cost_after = sum(
            self.lower_prop_damages_after) * (self.location_weight-1)
        self.upper_emergency_services_cost_after = sum(
            self.upper_prop_damages_after) * (self.location_weight-1)
        self.lower_annual_damage_after = sum(
            self.lower_prop_damages_after) + self.lower_emergency_services_cost_after
        self.upper_annual_damage_after = sum(
            self.upper_prop_damages_after) + self.upper_emergency_services_cost_after

        # Apply cumulative discount factors
        self.lower_lifetime_damage_after = (sum(self.lower_prop_damages_after) * self.df) + (
            self.lower_emergency_services_cost_after * self.health_df)
        self.upper_lifetime_damage_after = (sum(self.upper_prop_damages_after) * self.df) + (
            self.upper_emergency_services_cost_after * self.health_df)

        # Get benefits
        self.lower_benefit = self.lower_lifetime_damage - self.lower_lifetime_damage_after
        self.upper_benefit = self.upper_lifetime_damage - self.upper_lifetime_damage_after

    """
    RESULTS EXPORTING
    """

    def export_results(self, fname: str, export_options: List[bool], file_formats: List[bool]) -> None:
        """
        Export arg results to arg fname
        """
        # Build directories
        self.build_folders(fname, file_formats)

        # Write summary
        self.write_summary(fname, file_formats)

        export_funcs = [
            self.write_property_counts,
            self.write_existing_damages
        ]
        # Execute selected export functions
        for i in range(len(export_options)):
            if export_options[i]:
                export_funcs[i](fname, file_formats)

    def build_folders(self, fname: str, file_formats: List[bool]) -> None:
        """
        Create results folders in save location
        """
        csv_path = os.path.join(fname, "CSVs")
        xlsx_path = os.path.join(fname, "XLSXs")

        # Make parent folder if it doesn't exist
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
        """
        Write files containing summary of results
        """
        # Table headings
        dataset = [[None, "Properties at risk",
                    "Lower Annual Damage (£)", "Upper Annual Damage (£)"]]
        row_headers = const.initial_aeps + [None, None, None, None]

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

    def write_property_counts(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of properties damages in flood event
        """
        # Table headings
        dataset = [[None, "Properties at risk pre-intervention",
                    "Properties at risk post-intervention"]]
        row_headers = const.initial_aeps

        # Main data
        for i in range(6):
            row = [row_headers[i]] + \
                [self.props_at_risk[i], self.props_at_risk_after[i]]
            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Property Counts.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Property Counts.xlsx"))

    def write_existing_damages(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of existing damages
        """
        # Table headings
        dataset = [[None, "Properties at risk",
                    "Lower Annual Damage (£)", "Upper Annual Damage (£)"]]
        row_headers = const.initial_aeps + [None, None, None]

        # Main data
        main_data = self.get_pre_existing_datapoints()
        for i in range(len(row_headers)):
            row = [row_headers[i]] + main_data[i]
            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Existing Damages.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Existing Damages.xlsx"))
