# from src.pipelines.pipeline import run_research_pipeline

# topic = "The impact of AI on the job market in 2026"
# run_research_pipeline(topic)


# from src.agents.agents import llm
# print(llm.invoke("Say hello").content)

# from src.tools.tools import web_search
# print(web_search.invoke({"query": "AI jobs 2026"}))

from src.agents.agents import llm
print(llm.model)