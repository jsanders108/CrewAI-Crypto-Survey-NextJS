from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
import os
from pathlib import Path
import pandas as pd
from data_processing_tool import DataProcessingTool 
from crews.report_generation_crew.report_generation_crew import ReportGenerationCrew


class SurveyAnalyzerState(BaseModel):
    full_survey_data: str = ""
    processed_survey_results: str = ""
    final_report_results: str = ""


class SurveyAnalyzerFlow(Flow[SurveyAnalyzerState]):

    @start()
    def load_survey_data(self, survey_data): 
        # Store JSON string in the Pydantic object
        self.state.full_survey_data = survey_data

        print("Survey data successfully loaded into state.")


    @listen(load_survey_data)
    def process_survey_data(self):
        print("Processing survey data...")

        # Instantiate the tool
        tool = DataProcessingTool()

        # Run the tool with the loaded survey data
        result = tool._run(self.state.full_survey_data)

        # Store the processed output in the state variable
        self.state.processed_survey_results = result

        print("Survey data successfully processed.")
        return result

    @listen(process_survey_data)
    def generate_report(self):
        print("Generating report...")
        result = (
            ReportGenerationCrew()
            .crew()
            .kickoff(
                inputs={
                    "processed_survey_results": self.state.processed_survey_results
                }
            )
        )
        self.state.final_report_results = result.raw
        return self.state.final_report_results 


def kickoff(survey_data ):
    survey_analyzer_flow = SurveyAnalyzerFlow()
    # 1. Call the start step:
    survey_analyzer_flow.load_survey_data(
        survey_data=survey_data,
    ) 

    # 2. Then process the survey data:
    survey_analyzer_flow.process_survey_data()

    # 3. Then generate the report:
    return survey_analyzer_flow.generate_report() 
    


def plot():
    survey_flow = SurveyAnalyzerFlow()
    survey_flow.plot()


if __name__ == "__main__":
    kickoff()
