from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Model initialization
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)


# 1st Agent: Search Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a web research assistant. Use the web_search tool to find "
            "recent and reliable information. In your final answer, list the key "
            "findings and ALWAYS include the full URL of every source."
        ),
    )


# 2nd Agent: Reader Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a reading assistant. From the search results you are given, "
            "pick the 2 most relevant URLs and read them with the scrape_url tool. "
            "Return the key facts from each page together with its URL."
        ),
    )


# 3rd: Writer Chain
WRITER_SYSTEM_PROMPT = """You are an expert research report writer.
Write a clear, professional report using ONLY the research provided.
Do not invent facts, numbers or sources. If the research does not cover
something, say so instead of guessing.

The report MUST contain these sections, in this order, using Markdown headings:

# <Report Title>
## 1. Executive Summary  (3-5 sentences)
## 2. Introduction  (context and why the topic matters)
## 3. Key Findings  (bullet points, each backed by the research)
## 4. Detailed Analysis  (explain the findings, compare viewpoints)
## 5. Challenges and Limitations
## 6. Conclusion  (and recommendations or next steps)
## 7. Sources  (list every URL used from the research)

Keep the tone factual and the language simple."""

writer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", WRITER_SYSTEM_PROMPT),
        (
            "human",
            "Topic: {topic}\n\n"
            "Research material:\n{research}\n\n"
            "Write the full report now.",
        ),
    ]
)

writer_chain = writer_prompt | llm | StrOutputParser()


# 4th: Critic Chain
CRITIC_SYSTEM_PROMPT = """You are a strict but fair report reviewer.
Review the report you are given for accuracy, clarity, structure,
depth of analysis and use of sources. Do not rewrite the report.

Respond in EXACTLY this format and nothing else:

Score: <number>/10

Strengths:
- <strength 1>
- <strength 2>
- <strength 3>

Areas to Improve:
- <improvement 1>
- <improvement 2>
- <improvement 3>

Verdict: <one line verdict>"""

critic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CRITIC_SYSTEM_PROMPT),
        ("human", "Report to review:\n\n{report}"),
    ]
)

critic_chain = critic_prompt | llm | StrOutputParser()