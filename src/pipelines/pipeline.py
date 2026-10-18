# from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# def run_research_pipeline(topic: str)-> dict:

#     state = {}

#     #step 1 -search agent working
#     print("\n"+" = " *50)
#     print("step 1 - search agent is working...")
#     print("="*50)

#     search_agent = build_search_agent()
#     search_results = search_agent.invoke({
#         "messages": [("user",f"Find recent, reliable and detailed information about: {topic}")]
#     })

#     # state["search_results"]=search_results["messages"][-1].content
#     state["search_results"]=search_results["messages"][-1].text

#     print("\n search result ", state["search_results"])

#     #step 2 - reader agent working
#     print("\n"+" = " *50)   
#     print("step 2 - reader agent is scraping top resources...")
#     print("="*50)

#     reader_agent = build_reader_agent()
#     reader_results = reader_agent.invoke({
#         "messages": [("user",
#                       f"Based on the following search results about '{topic}',"
#                       f"pick the most relevant URL and scrape it for deeper content.\n\n"
#                       f"Search Results:\n {state['search_results'][:800]}"
#                     )]
#     })

#     # state['scraped_content']=reader_results["messages"][-1].content
#     state['scraped_content']=reader_results["messages"][-1].text

#     print("\nscraped content: \n", state['scraped_content'])

#     #step 3 - writer chain
#     print("\n"+"="*50)
#     print("step 3 - Writer is drafting the report...")
#     print("="*50)

#     research_combined=(
#         f"SEARCH RESULTS: \n {state['search_results']} \n\n"
#         f"DETAILED SCRAPED CONTENT: \n {state['scraped_content']}"
#     )

#     state["report"]=writer_chain.invoke({
#         "topic": topic,
#         "research": research_combined
#     })

#     print("\n Final Report\n", state["report"])


#     #step4: critic report
#     print("\n"+"="*50)
#     print("step 3 - Critic is reviewing the report...")
#     print("="*50)

#     state["feedback"]=critic_chain.invoke({
#         "report":state['report']
#         }
#     )

#     print("\n critic report \n", state["feedback"])


#     return state


from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str, on_step=None) -> dict:
    """Run search -> read -> write -> critique.

    on_step: optional function(message: str) called when each step starts.
             The Streamlit app uses it to show live progress.
    """

    def notify(message: str):
        if on_step:
            on_step(message)

    state = {}

    # step 1 - search agent
    print("\n" + "=" * 50)
    print("step 1 - search agent is working...")
    print("=" * 50)
    notify("🔎 Step 1: Search agent is finding sources...")

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_results["messages"][-1].text

    print("\n search result ", state["search_results"])

    # step 2 - reader agent
    print("\n" + "=" * 50)
    print("step 2 - reader agent is scraping top resources...")
    print("=" * 50)
    notify("📄 Step 2: Reader agent is scraping the best source...")

    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke({
        "messages": [("user",
                      f"Based on the following search results about '{topic}', "
                      f"pick the most relevant URL and scrape it for deeper content.\n\n"
                      f"Search Results:\n {state['search_results'][:800]}"
                      )]
    })
    state["scraped_content"] = reader_results["messages"][-1].text

    print("\nscraped content: \n", state["scraped_content"])

    # step 3 - writer chain
    print("\n" + "=" * 50)
    print("step 3 - Writer is drafting the report...")
    print("=" * 50)
    notify("✍️ Step 3: Writer is drafting the report...")

    research_combined = (
        f"SEARCH RESULTS: \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT: \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Final Report\n", state["report"])

    # step 4 - critic chain
    print("\n" + "=" * 50)
    print("step 4 - Critic is reviewing the report...")
    print("=" * 50)
    notify("🧐 Step 4: Critic is reviewing the report...")

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\n critic report \n", state["feedback"])

    return state



