from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import json
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

class DataProcessingToolInput(BaseModel):
    """
    Input schema for DataProcessingTool.
    The argument should be a JSON string representing the survey data,
    i.e. a list of dictionaries where each dictionary contains the survey
    responses for a single respondent.
    """
    argument: str = Field(
        ..., description="A JSON string containing the survey data. Each element in the list is a dictionary of responses."
    )

class DataProcessingTool(BaseTool):
    name: str = "SurveyAnalysisTool"
    description: str = (
        "This tool processes a list of JSON dictionaries representing survey data. "
        "It outputs frequency tables for each question, then for the first five questions "
        "it creates cross-tabulations with each of the last five demographic questions and "
        "performs chi-square analyses on each crosstab."
    )
    args_schema: Type[BaseModel] = DataProcessingToolInput

    def _run(self, argument: str) -> str:
        """
        Implementation of the survey analysis:
        1) Frequency tables for each question (there are 10 total).
        2) Crosstabs for each of the first five questions (Q1..Q5) with each of the last five questions (Q6..Q10).
        3) Chi-square test for each crosstab.
        Returns a string that contains all the results.
        """

        # Parse the JSON input into a Python list of dictionaries
        data = json.loads(argument)
        print(f"Total records received: {len(data)}")  # Debugging output

        # Create a DataFrame from the JSON data
        df = pd.DataFrame(data)
        print(f"Total records after conversion to DataFrame: {df.shape[0]}")  # Check if rows match

        if df.empty:
            return "Error: No data found after conversion. Please check the JSON structure."

        columns = df.columns.tolist()
        main_questions = columns[:5]      # Q1..Q5
        demographic_questions = columns[5:]  # Q6..Q10

        results = []

        # ---------------------
        # 1) FREQUENCY TABLES
        # ---------------------
        results.append("FREQUENCY TABLES FOR EACH QUESTION:\n")
        for col in columns:
            freq_table = df[col].value_counts(dropna=False)
            total_responses = freq_table.sum()
            print(f"Processing column: {col} | Total responses: {total_responses}")  # Debugging output

            results.append(f"Question: {col}")
            for index_val, count in freq_table.items():
                pct = (count / total_responses) * 100
                results.append(f"  {index_val} : {count} ({pct:.2f}%)")
            results.append("")  # blank line

        # ---------------------------------
        # 2) CROSSTABS AND CHI-SQUARE TESTS
        # ---------------------------------
        results.append("\nCROSSTAB TABLES AND CHI-SQUARE ANALYSES:\n")
        for mq in main_questions:
            for dq in demographic_questions:
                cross_tab = pd.crosstab(df[mq], df[dq])

                # Ensure the crosstab is valid before performing chi-square test
                if cross_tab.shape[0] > 1 and cross_tab.shape[1] > 1:
                    chi2, p_value, dof, expected = chi2_contingency(cross_tab)

                    results.append(f"Cross-tab of '{mq}' by '{dq}':")
                    results.append(str(cross_tab))
                    results.append("")
                    results.append(f"Chi-square test results:")
                    results.append(f"  chi2 statistic = {chi2:.4f}")
                    results.append(f"  p-value        = {p_value:.6f}")
                    results.append(f"  degrees of freedom = {dof}")
                    results.append("")
                else:
                    print(f"Skipping chi-square for {mq} x {dq} due to insufficient categories.")  # Debugging output

        return "\n".join(results)