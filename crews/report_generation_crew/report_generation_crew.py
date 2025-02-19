from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM
import os
from dotenv import load_dotenv



# Force reload the environment variables
load_dotenv(override=True)  # This will override existing variables


# Set the LLM to be used
openai_4o = LLM(model="gpt-4o", temperature=0)
openai_4o_mini = LLM(model="gpt-4o-mini", temperature=0)

openai_o1_preview= LLM(model="o1-preview")
openai_o1_mini = LLM(model="o1-mini")
openai_o1 = LLM(model="o1")
openai_o3_mini = LLM(model="o3-mini")

deepseek_r1 = LLM(
    model="openrouter/deepseek/deepseek-r1",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

deepseek_r1_free = LLM(
    model="openrouter/deepseek/deepseek-r1:free",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

deepseek_r1_distilled = LLM(
    model="openrouter/deepseek/deepseek-r1-distill-llama-70b",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


@CrewBase
class ReportGenerationCrew():
	"""ReportGeneration crew"""

	# The path to the configuration files
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def expert_market_research_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['expert_market_research_analyst'],
			verbose=True,
			llm=openai_4o_mini,
			allow_delegation=False
		)

	@agent
	def expert_market_research_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['expert_market_research_reviewer'],
			verbose=True,
			llm=openai_4o_mini,
			allow_delegation=False
		)

	@task
	def data_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['data_analysis_task'],
		)
	
	@task
	def review_task(self) -> Task:
		return Task(
			config=self.tasks_config['review_task'],
			output_file='final_report.md',
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ReportGenerationCrew crew"""

		return Crew(
			agents=self.agents, 
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True
		)
