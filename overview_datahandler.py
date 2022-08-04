"""
Data handling class for overview appraisals performed by Stix FAS 

Angus Toms 
14 06 2021
"""
import os
from typing import List

import const
import utils


class OverviewDataHandler():
    def __init__(self) -> None:
        # General flood information
        self.prop_count = 1
        self.warning = "No Warning"
        self.scheme_lifetime = 50
        self.location = "Urban"
        self.sop = 50

        self.df = 0
        self.health_df = 0
        self.location_weight = 0
        self.direct_damages = []

        # Existing Residential damages
        self.cumulative_res_counts = [0, 0, 0, 0, 0, 0, 0]
        self.res_counts = [0, 0, 0, 0, 0, 0, 0]
        self.lower_res_damages = [0, 0, 0, 0, 0, 0, 0]
        self.upper_res_damages = [0, 0, 0, 0, 0, 0, 0]
        self.lower_annual_res_damage = 0
        self.upper_annual_res_damage = 0
        self.lower_lifetime_res_damage = 0
        self.upper_lifetime_res_damage = 0

        # Residential benefits
        self.res_counts_after = [0, 0, 0, 0, 0, 0, 0]
        self.lower_res_damages_after = [0, 0, 0, 0, 0, 0, 0]
        self.upper_res_damages_after = [0, 0, 0, 0, 0, 0, 0]
        self.lower_annual_res_damage_after = 0
        self.upper_annual_res_damage_after = 0
        self.lower_lifetime_res_damage_after = 0
        self.upper_lifetime_res_damage_after = 0
        self.lower_res_benefit = 0
        self.upper_res_benefit = 0

        # Existing Non-Residential damages
        self.cumulative_non_res_counts = [
            [0, 0, 0, 0, 0, 0, 0] for _ in range(len(const.overview_non_res_mcm))]
        self.non_res_counts = [[0, 0, 0, 0, 0, 0, 0]
                               for _ in range(len(const.overview_non_res_mcm))]
        self.total_non_res_counts = [0, 0, 0, 0, 0, 0, 0]
        self.lower_non_res_damages = [[0, 0, 0, 0, 0, 0, 0]
                                      for _ in range(len(const.overview_non_res_mcm))]
        self.upper_non_res_damages = [[0, 0, 0, 0, 0, 0, 0]
                                      for _ in range(len(const.overview_non_res_mcm))]
        self.lower_total_non_res_damage = [0, 0, 0, 0, 0, 0, 0]
        self.upper_total_non_res_damage = [0, 0, 0, 0, 0, 0, 0]
        self.lower_annual_non_res_damage = 0
        self.upper_annual_non_res_damage = 0
        self.lower_lifetime_non_res_damage = 0
        self.upper_lifetime_non_res_damage = 0

        # Non-Residential benefits
        self.non_res_counts_after = [[0, 0, 0, 0, 0, 0, 0]
                                     for _ in range(len(const.overview_non_res_mcm))]
        self.total_non_res_counts_after = [0, 0, 0, 0, 0, 0, 0]
        self.lower_non_res_damages_after = [
            [0, 0, 0, 0, 0, 0, 0] for _ in range(len(const.overview_non_res_mcm))]
        self.upper_non_res_damages_after = [
            [0, 0, 0, 0, 0, 0, 0] for _ in range(len(const.overview_non_res_mcm))]
        self.lower_total_non_res_damage_after = [0, 0, 0, 0, 0, 0, 0]
        self.upper_total_non_res_damage_after = [0, 0, 0, 0, 0, 0, 0]
        self.lower_annual_non_res_damage_after = 0
        self.upper_annual_non_res_damage_after = 0
        self.lower_lifetime_non_res_damage_after = 0
        self.upper_lifetime_non_res_damage_after = 0
        self.lower_non_res_benefit = 0
        self.upper_non_res_benefit = 0

        # Totals pre-intervention
        self.lower_damages = [0, 0, 0, 0, 0, 0, 0]
        self.upper_damages = [0, 0, 0, 0, 0, 0, 0]
        self.lower_emergency_services_cost = 0
        self.upper_emergency_services_cost = 0
        self.lower_business_disruption = 0
        self.upper_business_disruption = 0
        self.lower_annual_damage = 0
        self.upper_annual_damage = 0
        self.lower_lifetime_damage = 0
        self.upper_lifetime_damage = 0

        # Totals post-intervention
        self.lower_damages_after = [0, 0, 0, 0, 0, 0, 0]
        self.upper_damages_after = [0, 0, 0, 0, 0, 0, 0]
        self.lower_emergency_services_cost_after = 0
        self.upper_emergency_services_cost_after = 0
        self.lower_business_disruption_after = 0
        self.upper_business_disruption_after = 0
        self.lower_annual_damage_after = 0
        self.upper_annual_damage_after = 0
        self.lower_lifetime_damage_after = 0
        self.upper_lifetime_damage_after = 0

        # Benefit totals
        self.lower_benefit = 0
        self.upper_benefit = 0

    """
    GENERAL METHODS
    """

    def remove_res_double_count(self) -> None:
        """
        Remove double count from cumulative res props
        """
        self.res_counts = [self.cumulative_res_counts[0]] + [
            self.cumulative_res_counts[i] - self.cumulative_res_counts[i-1] for i in range(1, 7)]

    def remove_non_res_double_count(self) -> None:
        """
        Remove double count from cumulative non res floor areas
        """
        for i in range(len(self.cumulative_non_res_counts)):
            self.non_res_counts[i] = [self.cumulative_non_res_counts[i][0]] + [
                self.cumulative_non_res_counts[i][j] - self.cumulative_non_res_counts[i][j-1] for j in range(1, 7)]

    def get_major_datapoints(self) -> List[List]:
        """
        Get 2d list of major datapoints to be displayed in summary tables
        """
        dataset_1 = [
            [self.res_counts_after[i],
             self.total_non_res_counts_after[i],
             self.lower_res_damages_after[i],
             self.upper_res_damages_after[i],
             self.lower_total_non_res_damage_after[i],
             self.upper_total_non_res_damage_after[i],
             self.lower_damages_after[i],
             self.upper_damages_after[i]] for i in range(7)]

        dataset_2 = [
            [sum(self.res_counts_after), sum(self.total_non_res_counts_after), "Annual Emergency Services Costs After (£)", None, None, None,
             self.lower_emergency_services_cost_after, self.upper_emergency_services_cost_after],
            [None, None, "Annual Business Disruption Costs After(£)", None, None, None,
             self.lower_business_disruption_after, self.upper_business_disruption_after],
            [None, None, "Average Annual Damage After (£)", None, None, None,
             self.lower_annual_damage_after, self.upper_annual_damage_after],
            [None, None, "Max Lifetime Damages After (£)", None, None, None, self.lower_lifetime_damage_after,
             self.upper_lifetime_damage_after],
            [None, None, "Lifetime Benefit (£)", None, None, None,
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
        # Res damages and benefits
        self.get_existing_res_damages()
        self.get_res_benefits()

        # Non-res damages and benefits
        self.get_existing_non_res_damages()
        self.get_non_res_benefits()

        # Totals
        self.get_totals()

    def get_existing_res_damages(self) -> None:
        """
        Calculate existing residential damages arising from flood events
        """
        # Get general flood info
        self.direct_damages = utils.get_damage_per_prop(self.warning)
        self.location_weight = utils.get_location_weight(self.location)
        self.df = utils.get_cumulative_discount_factor(self.scheme_lifetime)
        self.health_df = utils.get_cumulative_health_discount_factor(
            self.scheme_lifetime)

        # Damages
        self.lower_res_damages = [self.res_counts[i]
                                  * self.direct_damages[i+1] for i in range(7)]
        self.upper_res_damages = [self.res_counts[i]
                                  * self.direct_damages[i] for i in range(7)]
        self.lower_annual_res_damage = sum(self.lower_res_damages)
        self.upper_annual_res_damage = sum(self.upper_res_damages)

        # Apply cumulative discount factors
        self.lower_lifetime_res_damage = self.lower_annual_res_damage * self.df
        self.upper_lifetime_res_damage = self.upper_annual_res_damage * self.df

    def get_res_benefits(self) -> None:
        """
        Calculate benefits arising from flood intervention
        """
        # Get property counts
        self.res_counts_after = self.res_counts.copy()
        if self.sop == 200:
            self.res_counts_after = [0, 0, 0, 0, 0, 0, 0]
        else:
            for i in range(7):
                if const.overview_return_periods[i] <= self.sop:
                    self.res_counts_after[i+1] += self.res_counts_after[i]
                    self.res_counts_after[i] = 0

        # Get damages
        self.lower_res_damages_after = [
            self.res_counts_after[i]*self.direct_damages[i+1] for i in range(7)]
        self.upper_res_damages_after = [
            self.res_counts_after[i]*self.direct_damages[i] for i in range(7)]
        self.lower_annual_res_damage_after = sum(self.lower_res_damages_after)
        self.upper_annual_res_damage_after = sum(self.upper_res_damages_after)

        # Apply cumulative discount factors
        self.lower_lifetime_res_damage_after = self.lower_annual_res_damage_after * self.df
        self.upper_lifetime_res_damage_after = self.upper_annual_res_damage_after * self.df

        # Get benefits
        self.lower_res_benefit = self.lower_lifetime_res_damage - \
            self.lower_lifetime_res_damage_after
        self.upper_res_benefit = self.upper_lifetime_res_damage - \
            self.upper_lifetime_res_damage_after

    def get_existing_non_res_damages(self) -> None:
        """
        Calculate existing non-residential damages arising from flood events
        """
        # Damages
        for i in range(len(const.overview_non_res_mcm)):
            for j in range(7):
                self.lower_non_res_damages[i][j] = self.non_res_counts[i][j] * \
                    const.damage_per_non_res_prop[i][j+1]
                self.upper_non_res_damages[i][j] = self.non_res_counts[i][j] * \
                    const.damage_per_non_res_prop[i][j]

        # Totals
        self.total_non_res_counts = [sum([self.non_res_counts[i][j] for i in range(
            len(const.overview_non_res_mcm))]) for j in range(7)]
        self.lower_total_non_res_damage = [sum([self.lower_non_res_damages[i][j] for i in range(
            len(const.overview_non_res_mcm))]) for j in range(7)]
        self.upper_total_non_res_damage = [sum([self.upper_non_res_damages[i][j] for i in range(
            len(const.overview_non_res_mcm))]) for j in range(7)]
        self.lower_annual_non_res_damage = sum(self.lower_total_non_res_damage)
        self.upper_annual_non_res_damage = sum(self.upper_total_non_res_damage)

        # Apply cumulative discount factors
        self.lower_lifetime_non_res_damage = self.lower_annual_non_res_damage * self.df
        self.upper_lifetime_non_res_damage = self.upper_annual_non_res_damage * self.df

    def get_non_res_benefits(self) -> None:
        """
        Calculate benefits arising from flood intervention
        """
        # Get property counts
        # List comprehension required for shallow copy of 2d list
        self.non_res_counts_after = [row[:] for row in self.non_res_counts]
        if self.sop == 200:
            self.non_res_counts_after = [[0, 0, 0, 0, 0, 0, 0]
                                         for _ in range(len(const.overview_non_res_mcm))]

        else:
            for i in range(len(const.overview_non_res_mcm)):
                # Iterate through property types
                for j in range(7):
                    # Iterate through return periods
                    if const.overview_return_periods[j] <= self.sop:
                        self.non_res_counts_after[i][j +
                                                     1] += self.non_res_counts_after[i][j]
                        self.non_res_counts_after[i][j] = 0

        # Get damages
        for i in range(len(const.overview_non_res_mcm)):
            for j in range(7):
                self.lower_non_res_damages_after[i][j] = self.non_res_counts_after[i][j] * \
                    const.damage_per_non_res_prop[i][j+1]
                self.upper_non_res_damages_after[i][j] = self.non_res_counts_after[i][j] * \
                    const.damage_per_non_res_prop[i][j]

        # Totals
        self.total_non_res_counts_after = [sum([self.non_res_counts_after[i][j] for i in range(
            len(const.overview_non_res_mcm))]) for j in range(7)]
        self.lower_total_non_res_damage_after = [sum([self.lower_non_res_damages_after[i][j] for i in range(
            len(const.overview_non_res_mcm))]) for j in range(7)]
        self.upper_total_non_res_damage_after = [sum([self.upper_non_res_damages_after[i][j] for i in range(
            len(const.overview_non_res_mcm))]) for j in range(7)]
        self.lower_annual_non_res_damage_after = sum(
            self.lower_total_non_res_damage_after)
        self.upper_annual_non_res_damage_after = sum(
            self.upper_total_non_res_damage_after)

        # Apply cumulative discount factors
        self.lower_lifetime_non_res_damage_after = self.lower_annual_non_res_damage_after * self.df
        self.upper_lifetime_non_res_damage_after = self.upper_annual_non_res_damage_after * self.df

        # Get benefits
        self.lower_non_res_benefit = self.lower_lifetime_non_res_damage - \
            self.lower_lifetime_non_res_damage_after
        self.upper_non_res_benefit = self.upper_lifetime_non_res_damage - \
            self.lower_lifetime_non_res_damage_after

    def get_totals(self) -> None:
        """
        Sum residential and non-residential damages and benefits
        """
        # Pre-intervention
        self.lower_damages = [self.lower_res_damages[i] +
                              self.lower_total_non_res_damage[i] for i in range(7)]
        self.upper_damages = [self.upper_res_damages[i] +
                              self.upper_total_non_res_damage[i] for i in range(7)]
        self.lower_emergency_services_cost = sum(
            self.lower_damages) * (self.location_weight - 1)
        self.upper_emergency_services_cost = sum(
            self.upper_damages) * (self.location_weight - 1)
        self.lower_business_disruption = sum(
            self.lower_total_non_res_damage) * 0.03
        self.upper_business_disruption = sum(
            self.upper_total_non_res_damage) * 0.03
        self.lower_annual_damage = sum(
            self.lower_damages) + self.lower_emergency_services_cost + self.lower_business_disruption
        self.upper_annual_damage = sum(
            self.upper_damages) + self.upper_emergency_services_cost + self.upper_business_disruption
        self.lower_lifetime_damage = ((sum(self.lower_damages) + self.lower_business_disruption)
                                      * self.df) + (self.lower_emergency_services_cost * self.health_df)
        self.upper_lifetime_damage = ((sum(self.upper_damages) + self.upper_business_disruption)
                                      * self.df) + (self.upper_emergency_services_cost * self.health_df)

        # Post-intervention
        self.lower_damages_after = [
            self.lower_res_damages_after[i] + self.lower_total_non_res_damage_after[i] for i in range(7)]
        self.upper_damages_after = [
            self.upper_res_damages_after[i] + self.upper_total_non_res_damage_after[i] for i in range(7)]
        self.lower_emergency_services_cost_after = sum(
            self.lower_damages_after) * (self.location_weight - 1)
        self.upper_emergency_services_cost_after = sum(
            self.upper_damages_after) * (self.location_weight - 1)
        self.lower_business_disruption_after = sum(
            self.lower_total_non_res_damage_after) * 0.03
        self.upper_business_disruption_after = sum(
            self.upper_total_non_res_damage_after) * 0.03
        self.lower_annual_damage_after = sum(
            self.lower_damages_after) + self.lower_emergency_services_cost_after + self.lower_business_disruption_after
        self.upper_annual_damage_after = sum(
            self.upper_damages_after) + self.upper_emergency_services_cost_after + self.upper_business_disruption_after

        self.lower_lifetime_damage_after = ((sum(self.lower_damages_after) + self.lower_business_disruption_after)
                                            * self.df) + (self.lower_emergency_services_cost_after * self.health_df)
        self.upper_lifetime_damage_after = ((sum(self.upper_damages_after) + self.upper_business_disruption_after)
                                            * self.df) + (self.upper_emergency_services_cost_after * self.health_df)

        # Benefits
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
            self.write_pre_intervention_res,
            self.write_post_intervention_res,
            self.write_pre_intervention_non_res,
            self.write_post_intervention_non_res,
            self.write_pre_intervention_property_counts,
            self.write_post_intervention_property_counts
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
        """
        Write files containing summary of results
        """
        # Table headings
        dataset = [[None, "Residential Properties at risk",
                    "Non-Residential Floor Area at risk (m²)", "Lower Residential Damage (£)",
                    "Upper Residential Damage (£)", "Lower Non-Residential Damage (£)", "Upper Non-Residential Damage (£)", "Lower Total Damage (£)", "Upper Total Damage (£)"]]
        row_headers = const.overview_aeps

        # Main data
        for i in range(7):
            dataset.append([row_headers[i], self.res_counts_after[i], self.total_non_res_counts_after[i], self.lower_res_damages_after[i], self.upper_res_damages_after[i],
                           self.lower_total_non_res_damage_after[i], self.upper_total_non_res_damage_after[i], self.lower_damages_after[i], self.upper_damages_after[i]])

        # Add totals
        dataset.append(["Totals", sum(self.res_counts_after), sum(self.total_non_res_counts_after), None, None, None,
                       "Annual Emergency Services Cost After (£)", self.lower_emergency_services_cost_after, self.upper_emergency_services_cost_after])
        dataset.append([None, None, None, None, None, None, "Annual Business Disruption Costs After (£)",
                       self.lower_business_disruption_after, self.upper_business_disruption_after])
        dataset.append([None, None, None, None, None, None, "Average Annual Damage After (£)",
                       self.lower_annual_damage_after, self.upper_annual_damage_after])
        dataset.append([None, None, None, None, None, None, "Max Lifetime Damages After (£)",
                       self.lower_lifetime_damage_after, self.upper_lifetime_damage_after])
        dataset.append([None, None, None, None, None, None,
                       "Lifetime Benefit After (£)", self.lower_benefit, self.upper_benefit])

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Results Summary.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Results Summary.xlsx"))

    def write_pre_intervention_res(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of pre-intervention residential damages
        """
        # Table headings
        dataset = [
            ["Return Period", "Lower Annual Damage (£)", "Upper Annual Damage (£)"]]
        row_headings = const.overview_aeps

        # Main data
        for i in range(7):
            dataset.append([row_headings[i], self.lower_res_damages[i],
                            self.upper_res_damages[i]])

        # Add totals
        dataset.append(["Total Average Annual Damage (£)",
                        self.lower_annual_res_damage, self.upper_annual_res_damage])
        dataset.append(["Max Lifetime Damage (£)", self.lower_lifetime_res_damage,
                        self.upper_lifetime_res_damage])

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Pre-intervention res.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Pre-intervention res.xlsx"))

    def write_post_intervention_res(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write file containing breakdown of post-intervention residential damages
        """
        # Table headings
        dataset = [
            ["Return Period", "Lower Annual Damage (£)", "Upper Annual Damage (£)"]]
        row_headings = const.overview_aeps

        # Main data
        for i in range(7):
            dataset.append([row_headings[i], self.lower_res_damages_after[i],
                            self.upper_res_damages_after[i]])

        # Add totals
        dataset.append(["Total Average Annual Damage After (£)",
                        self.lower_annual_res_damage_after, self.upper_annual_res_damage_after])
        dataset.append(["Max Lifetime Damage After (£)", self.lower_lifetime_res_damage_after,
                        self.upper_lifetime_res_damage_after])
        dataset.append(["Lifetime Benefit After (£)",
                        self.lower_res_benefit, self.upper_res_benefit])

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Post-intervention res.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Post-intervention res.xlsx"))

    def write_pre_intervention_non_res(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of pre-intervention non-residential damages
        """
        # Table headings
        dataset = [["Return Period"]]
        for mcm in const.overview_non_res_mcm:
            dataset[0] += [f"{mcm} Lower Damage (£)",
                           f"{mcm} Upper Damage (£)"]
        row_headings = const.overview_aeps

        # Main data
        for i in range(7):
            row = [row_headings[i]]
            for j in range(len(const.overview_non_res_mcm)):
                row.append(self.lower_non_res_damages[j][i])
                row.append(self.upper_non_res_damages[j][i])

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Pre-intervention non res.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Pre-intervention non res.xlsx"))

    def write_post_intervention_non_res(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of post-intervention non-residential damages
        """
        # Table headings
        dataset = [["Return Period"]]
        for mcm in const.overview_non_res_mcm:
            dataset[0] += [f"{mcm} Lower Damage (£)",
                           f"{mcm} Upper Damage (£)"]
        row_headings = const.overview_aeps

        # Main data
        for i in range(7):
            row = [row_headings[i]]
            for j in range(len(const.overview_non_res_mcm)):
                row.append(self.lower_non_res_damages_after[j][i])
                row.append(self.upper_non_res_damages_after[j][i])

            dataset.append(row)

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Post-intervention non res.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Post-intervention non res.xlsx"))

    def write_pre_intervention_property_counts(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of pre-intervention property counts
        """
        # Table headings
        dataset = [[None, "Residential Properties at risk"] +
                   [f"{mcm} Floor Area at risk (m²)" for mcm in const.overview_non_res_mcm]]
        row_headings = const.overview_aeps

        # Main data
        for i in range(7):
            dataset.append([row_headings[i], self.res_counts[i]] + [self.non_res_counts[j][i]
                           for j in range(len(const.overview_non_res_mcm))])

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Pre-intervention property counts.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Pre-intervention property counts.xlsx"))

    def write_post_intervention_property_counts(self, fname: str, file_formats: List[bool]) -> None:
        """
        Write files containing breakdown of post-intervention property counts
        """
        # Table headings
        dataset = [[None, "Residential Properties at risk"] +
                   [f"{mcm} Floor Area at risk (m²)" for mcm in const.overview_non_res_mcm]]
        row_headings = const.overview_aeps

        # Main data
        for i in range(7):
            dataset.append([row_headings[i], self.res_counts_after[i]] + [
                           self.non_res_counts_after[j][i] for j in range(len(const.overview_non_res_mcm))])

        if file_formats[0]:
            # Write .csv
            utils.list_to_csv(dataset, os.path.join(
                fname, "CSVs/Post-intervention property counts.csv"))

        if file_formats[1]:
            # Write .xlsx
            utils.list_to_xlsx(dataset, os.path.join(
                fname, "XLSXs/Post-intervention property counts.xlsx"))
