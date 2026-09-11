import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import random
import time
from tavily import TavilyClient

load_dotenv()

print("PROMPT RELAY ORCHESTRATOR\n")

MODEL_TO_CATEOGRY={
    "1":"Openrouter",
    "2":"Nvidia"
}

while True:
    provider=input("""CHOOSE YOUR AI MODEL-
        1. Openrouter (Recommended)
        2. Nvidia       
        """).strip()
    
    if provider in MODEL_TO_CATEOGRY:
        provider=MODEL_TO_CATEOGRY[provider]
    else:
        provider=provider.capitalize()

    if provider in ["Openrouter","Nvidia"]:
        break
    print("Not a valid option, try again")

MODEL_CATEGORIES={ 
    "Speed":["nvidia/nemotron-3.5-lightning:free", "liquid/lfm-2.5-2.6b:free", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free","google/gemma-4-26b-a4b-it:free"],
    "Research":["nvidia/nemotron-3-ultra-550b-a55b:free", "google/gemma-4-31b-it:free"],
    "Coding":["poolside/laguna-s-2.1:free", "poolside/laguna-xs-2.1:free", "cohere/north-mini-code:free"],
    "Business":["nvidia/nemotron-3-super-120b-a12b:free", "google/gemma-4-26b-a4b-it:free", ]
}

MODEL_CATEGORIES_NVIDIA={
    "Speed":["nvidia/nemotron-3-nano-omni-30b-a3b-reasoning","google/gemma-4-31b-it","openai/gpt-oss-20b"],
    "Research":["deepseek-ai/deepseek-v4-flash-0731", "deepseek-ai/deepseek-v4-pro-0813","moonshotai/kimi-k3","nvidia/nemotron-3-ultra-550b-a55b","google/diffusiongemma-26b-a4b-it"],
    "Coding":["poolside/laguna-xs-2.1", "nvidia/nemotron-3-ultra-550b-a55b","mistralai/mistral-nemotron","nvidia/nemotron-3-super-120b-a12b","google/diffusiongemma-26b-a4b-it"],
    "Business":["nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "google/gemma-4-31b-it","openai/gpt-oss-20b","nvidia/nemotron-3-super-120b-a12b"]
}

FREE_MODELS=[
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "liquid/lfm-2.5-2.6b:free",
    "google/gemma-4-26b-a4b-it:free"
]

FREE_MODELS_NVIDIA = [
    "google/diffusiongemma-26b-a4b-it",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "google/gemma-4-31b-it",
    "openai/gpt-oss-20b"
]

FREE_MODELS_GROQ=[
    "openai/gpt-oss-20b",
    "groq/compound-mini",
    "groq/compound",
    "openai/gpt-oss-120b"
]

if provider=="Openrouter":
    chosen_base_url="https://openrouter.ai/api/v1"
    chosen_api_key=os.getenv("OPENROUTER_API_KEY")
    cateogry=MODEL_CATEGORIES
    improver=FREE_MODELS
else:
    chosen_base_url="https://integrate.api.nvidia.com/v1"
    chosen_api_key=os.getenv("NVIDIA_API_KEY")
    cateogry=MODEL_CATEGORIES_NVIDIA
    improver=FREE_MODELS_NVIDIA

NUMBER_TO_CATEGORY={
    "1":"Speed",
    "2":"Research",
    "3":"Coding",
    "4":"Business"
    }

summarised_data=[]
full_history=[]
conversation_history=[]
conversation_questions=[]
previous_question="This is the very first message."
token_used=0
history_points=0

while True:
    priority=input("""What is your priority?
    1. Speed
    2. Research
    3. Coding
    4. Business
    """).strip()
    
    if priority in NUMBER_TO_CATEGORY:
        priority=NUMBER_TO_CATEGORY[priority]
    else:
        priority=priority.capitalize()

    if priority in cateogry:
        break
    print("Not a valid option,try again")

chosen_category=cateogry[priority]

print("Hello! How can I help you today? ")

while True:
    user_input=input("You: ")
    print("\nDEBUGGING-", user_input)

    start=time.time()

    available_improvers=list(improver)
    prompt_success=False

    while available_improvers:
        chosen_model2=random.choice(available_improvers)

        try:
            llm=ChatOpenAI(
            model=chosen_model2,
            base_url=chosen_base_url,
            api_key=chosen_api_key
            )

            inner_attempts=0
            max_inner_attempts=3
            while inner_attempts<max_inner_attempts:        
                response=llm.invoke([
                    ("system", f"""You are a prompt improver.ONLY print the single best improved prompt nothing else.
                    To help you understand context, the last question which the AI asked the user is:
                    {previous_question}

                    Rewrite the user's message into a clearer, more concise prompt.
                    Do not answer the request — output ONLY the single best improved prompt and nothing else.

                Example:
                Input: "Explain Elon Musk and Jeff Bezos connection to daily trade actually leave out Jeff Bezos and include finance too"
                Output: "Establish Elon Musks connection with daily trade and finance"
                """),
                    ("user", user_input)
                ])

                improved_prompt=response.content

                if "<|" in improved_prompt:
                    print("THE MODEL THREW AN ERROR RETRYING.")
                    inner_attempts+=1
                    if inner_attempts==max_inner_attempts:
                        available_improvers.remove(chosen_model2)
                        break
                else:
                    conversation_history.append(("user", improved_prompt))
                    full_history.append(("user", improved_prompt))
                    print("\nImproved Prompt:")
                    print(improved_prompt)
                    prompt_success=True
                    history_points+=1
                    break
            if prompt_success==True:  
                break  
               
        except Exception as e:
            print(f"Model {chosen_model2} failed at the task({e}).\nRetrying with another model ")
            available_improvers.remove(chosen_model2)
            
    if not prompt_success:
        print("ALL PRIMARY IMPROVER MODELS FAILED. SWITCHING TO GROQ.")
        groq_improvers=list(FREE_MODELS_GROQ)

        while groq_improvers:
            chosen_model3=random.choice(groq_improvers)
            try:
                groq_improver_llm=ChatOpenAI(
                    model=chosen_model3,
                    base_url="https://api.groq.com/openai/v1",
                    api_key=os.getenv("GROQ_API_KEY")
                )

                response = groq_improver_llm.invoke([
                        ("system", f"""You are a prompt improver.ONLY print the single best improved prompt nothing else.
                        To help you understand context, the last question which the AI asked the user is:
                        {previous_question}

                        Rewrite the user's message into a clearer, more concise prompt.
                        Do not answer the request — output ONLY the single best improved prompt and nothing else.

                Example:
                Input: "Explain Elon Musk and Jeff Bezos connection to daily trade actually leave out Jeff Bezos and include finance too"
                Output: "Establish Elon Musks connection with daily trade and finance"
                """),
                    ("user", user_input)
                ])

                improved_prompt=response.content
                conversation_history.append(("user", improved_prompt))
                full_history.append(("user", improved_prompt))
                print(f"\nImproved Prompt:")
                print(improved_prompt)
                prompt_success=True
                history_points+=1
                break

            except Exception as e:
                print(f"Groq model {chosen_model3} failed at the task ({e}). Retrying with another Groq model.")
                groq_improvers.remove(chosen_model3)

    if not prompt_success:
        print(f"ALL IMPROVERS INCLUDING GROQ FAILED. USING ORIGNAL RAW OUTPUT.")
        conversation_history.append(("user", user_input))
        full_history.append(("user", user_input))
        history_points+=1   

    max_retries=len(chosen_category)
    attempts=0

    while attempts<max_retries:   
        chosen_model=random.choice(chosen_category)
        print(f"Selected {chosen_model} for answering the user")

        try:
            answer_llm= ChatOpenAI(
                model=chosen_model,
                base_url=chosen_base_url,
                api_key=chosen_api_key
            )

            searching=True
            searches=0
            max_searches=3
            while searching and searches<max_searches:

                final_response=answer_llm.invoke(
                    [("system", """Answer the user's question clearly and helpfully.
                    End your response with one relevant follow-up question to continue the conversation naturally. 
                    Here is the history of the conversation aiding you in understanding the context
                    If you need current information to answer the user, or if the user specifically asks for a web search respond with exactly SEARCH:<your query> nothing else, otherwise just answer normally.""")]+conversation_history
                    )
                search_final_response=final_response.content.strip()
                if "SEARCH:" in search_final_response:
                    query=search_final_response.removeprefix("SEARCH:")
                    tavilyclient=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                    response=tavilyclient.search(query)

                    query_results=response["results"]

                    for query_result in query_results:
                        data1=query_result["title"]
                        data2=query_result["content"]
                        total_data=("SEARCH RESULTS"+data1+" "+data2)
                        conversation_history.append(("user",total_data))

                    web_results_analyzed=answer_llm.invoke(
                        [("system", """Answer the user's question clearly and helpfully.
                    End your response with one relevant follow-up question to continue the conversation naturally.
                    If you need current information to answer the user, or if the user specifically asks for a web search respond with exactly SEARCH:<your query> nothing else, otherwise just answer normally.
                    If search results are already present them use instead of searching again.
                    Here is the history of the conversation aiding you in understanding the context.""")]+conversation_history
                    )
                    conversation_history.append(("assistant", web_results_analyzed.content))
                    full_history.append(("assistant", web_results_analyzed.content))
                    print("\nFINAL ANSWER")
                    print(web_results_analyzed.content)
                    token_used+=final_response.usage_metadata["total_tokens"]+web_results_analyzed.usage_metadata["total_tokens"]
                    searches+=1
                    history_points+=len(query_results)+1
                    searching=False

                else:
                    conversation_history.append(("assistant", final_response.content))
                    full_history.append(("assistant", final_response.content))
                    print("\nFINAL ANSWER")
                    print(final_response.content)
                    token_used+=final_response.usage_metadata["total_tokens"]
                    history_points+=1
                    searching=False
            break        

        except Exception as e:
            print(f"Model {chosen_model} failed at the task({e}).Retrying with another model ")
            chosen_category.remove(chosen_model)
            attempts+=1

    full_text=conversation_history[-1][1]
    clean_text=full_text.strip()
    paragraphs=clean_text.split("\n\n")
    previous_question=paragraphs[-1].strip()
    conversation_questions.append(previous_question)

    end=time.time()
    duration=end-start
    print(f"Response took {duration:.2f} seconds")
    print(f"Response took {token_used} tokens")

    if history_points>=6:

        answer_llm= ChatOpenAI(
            model=chosen_model,
            base_url=chosen_base_url,
            api_key=chosen_api_key
        )

        summary=answer_llm.invoke(
            [("system","Summarize the conversation so far. Split the summary into two clear sections: user questions and AI responses.")]+conversation_history
        )
        summary_data=summary.content
        summarised_data.append(summary_data)
        conversation_history=[("assistant", f"Summary of previous context is {summary_data}")]
        history_points=1