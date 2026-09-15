import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import random
import time
from tavily import TavilyClient
from pydantic import BaseModel,Field
from typing import List,Union,Literal

load_dotenv()

print("PROMPT RELAY ORCHESTRATOR\n")

MODEL_TO_CATEOGRY={
    "1":"Openrouter",
    "2":"Nvidia"
}

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

global_fallback_openrouter=[
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "google/gemma-4-31b-it:free",
    "poolside/laguna-s-2.1:free",
    "poolside/laguna-xs-2.1:free",
    "cohere/north-mini-code:free",
    "nvidia/nemotron-3-super-120b-a12b:free"]

global_fallback_nvidia=[
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "google/gemma-4-31b-it",
    "openai/gpt-oss-20b",
    "deepseek-ai/deepseek-v4-flash-0731",
    "deepseek-ai/deepseek-v4-pro-0813",
    "moonshotai/kimi-k3",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "google/diffusiongemma-26b-a4b-it",
    "poolside/laguna-xs-2.1",
    "mistralai/mistral-nemotron",
    "nvidia/nemotron-3-super-120b-a12b"]

class SearchRequest(BaseModel):
    action:Literal["search"]="search"
    query_to_tavily:str=Field(
        description="The search query."
    )

class DirectAnswer(BaseModel):
    action:Literal["answer"]="answer"
    final_answer:str=Field(
        description="The final answer to the user."
    )
    question_asked:str=Field(
        description="The question asked to the user to keep the conversation going."
    )

class FinalLlmAnswer(BaseModel):
    decision: Union[SearchRequest,DirectAnswer]=Field(discriminator="action")

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

if provider=="Openrouter":
    chosen_base_url="https://openrouter.ai/api/v1"
    chosen_api_key=os.getenv("OPENROUTER_API_KEY")
    cateogry=MODEL_CATEGORIES
    improver=FREE_MODELS
    global_fallback=global_fallback_openrouter
else:
    chosen_base_url="https://integrate.api.nvidia.com/v1"
    chosen_api_key=os.getenv("NVIDIA_API_KEY")
    cateogry=MODEL_CATEGORIES_NVIDIA
    improver=FREE_MODELS_NVIDIA
    global_fallback=global_fallback_nvidia

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
search_results=[]
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
    active_model=None
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
                    Do not answer the request output ONLY the single best improved prompt and nothing else.

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

    available_answerers=list(chosen_category)
    answer_success=False

    while available_answerers:   
        chosen_model=random.choice(available_answerers)
        print(f"Selected {chosen_model} for answering the user")

        try:
            answer_llm= ChatOpenAI(
                model=chosen_model,
                base_url=chosen_base_url,
                api_key=chosen_api_key
            )
            structured_final_answer=answer_llm.with_structured_output(FinalLlmAnswer, include_raw=True)
            response=structured_final_answer.invoke(
                [("system","""You are an AI assistant.
                Decide whether u need to run a live web search for answering the user accurately or if you can provide a direct answer.
                End your response with one relevant question if you decide not to search and want to continue the conversation naturally.
                Here is the history of the conversation helping you to understand context.""")]+conversation_history)
                
            if response["parsed"] is None:
                print(f"Model {chosen_model} threw an error. Retrying with another model.")
                available_answerers.remove(chosen_model)
                continue

            decision_object=response["parsed"].decision
            tokens_from_router=response["raw"].usage_metadata["total_tokens"]
            
            if isinstance(decision_object,SearchRequest):
                query=decision_object.query_to_tavily
                tavilyclient=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                tavily_response=tavilyclient.search(query)
                query_results=tavily_response["results"]

                for query_result in query_results:
                    data1=query_result["title"]
                    data2=query_result["content"]
                    total_data=("SEARCH RESULTS"+" "+data1+" "+data2)
                    search_results.append(("user", total_data))

                web_results_analyzed=answer_llm.invoke(
                    [("system", """Answer the user's question clearly and helpfully.
                End your response with one relevant follow-up question to continue the conversation naturally.
                Here is the history of the conversation aiding you in understanding the context.""")]+search_results+conversation_history
                )
                conversation_history.append(("assistant", web_results_analyzed.content))
                full_history.append(("assistant", web_results_analyzed.content))
                print("\nFINAL ANSWER")
                print(web_results_analyzed.content)
                token_used+=tokens_from_router+web_results_analyzed.usage_metadata["total_tokens"]
                history_points+=1  
                end=time.time()
                duration=end-start
                print(f"Response took {duration:.2f} seconds")
                print(f"Total tokens used are {token_used}.")
                answer_success=True

            elif isinstance(decision_object,DirectAnswer):
                final_text=decision_object.final_answer
                conversation_history.append(("assistant", final_text))
                full_history.append(("assistant", final_text))
                print("\nFINAL ANSWER")
                print(final_text)
                token_used+=tokens_from_router
                history_points+=1
                previous_question=decision_object.question_asked
                conversation_questions.append(previous_question)
                end=time.time()
                duration=end-start
                print(f"Response took {duration:.2f} seconds")
                print(f"Total tokens used are {token_used}.")
                answer_success=True
            
            if answer_success==True:
                active_model=chosen_model
                break                                                    
        except Exception as e:
            print(f"Model {chosen_model} failed at the task({e}).Retrying with another model ")
            available_answerers.remove(chosen_model)
    if not answer_success:
        print("ALL MODELS FROM THE DESIGNATED CATEOGRY FAILED. SWITCHING TO GLOBAL FALLBACK POOL OF MODELS.")
        answer_fallback=list(global_fallback)

        while answer_fallback:
            chosen_model4=random.choice(answer_fallback)
            try:
                answer_llm= ChatOpenAI(
                    model=chosen_model4,
                    base_url=chosen_base_url,
                    api_key=chosen_api_key
                )
                structured_final_answer=answer_llm.with_structured_output(FinalLlmAnswer, include_raw=True)
                response=structured_final_answer.invoke(
                    [("system","""You are an AI assistant.
                    Decide whether u need to run a live web search for answering the user accurately or if you can provide a direct answer.
                    End your response with one relevant question if you decide not to search and want to continue the conversation naturally.
                    Here is the history of the conversation helping you to understand context.""")]+conversation_history)
                    
                if response["parsed"] is None:
                    print(f"Model {chosen_model4} threw an error. Retrying with another model.")
                    answer_fallback.remove(chosen_model4)
                    continue

                decision_object=response["parsed"].decision
                tokens_from_router=response["raw"].usage_metadata["total_tokens"]
                
                if isinstance(decision_object,SearchRequest):
                    query=decision_object.query_to_tavily
                    tavilyclient=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                    tavily_response=tavilyclient.search(query)
                    query_results=tavily_response["results"]

                    for query_result in query_results:
                        data1=query_result["title"]
                        data2=query_result["content"]
                        total_data=("SEARCH RESULTS"+" "+data1+" "+data2)
                        search_results.append(("user",total_data)) 

                    web_results_analyzed=answer_llm.invoke(
                        [("system", """Answer the user's question clearly and helpfully.
                    End your response with one relevant follow-up question to continue the conversation naturally.
                    Here is the history of the conversation aiding you in understanding the context.""")]+search_results+conversation_history
                    )
                    conversation_history.append(("assistant", web_results_analyzed.content))
                    full_history.append(("assistant", web_results_analyzed.content))
                    print("\nFINAL ANSWER")
                    print(web_results_analyzed.content)
                    token_used+=tokens_from_router+web_results_analyzed.usage_metadata["total_tokens"]
                    history_points+=len(query_results)+1  
                    end=time.time()
                    duration=end-start
                    print(f"Response took {duration:.2f} seconds")
                    print(f"Total tokens used are {token_used}.")
                    answer_success=True

                elif isinstance(decision_object,DirectAnswer):
                    final_text=decision_object.final_answer
                    conversation_history.append(("assistant", final_text))
                    full_history.append(("assistant", final_text))
                    print("\nFINAL ANSWER")
                    print(final_text)
                    token_used+=tokens_from_router
                    history_points+=1
                    previous_question=decision_object.question_asked
                    conversation_questions.append(previous_question)
                    end=time.time()
                    duration=end-start
                    print(f"Response took {duration:.2f} seconds")
                    print(f"Total tokens used are {token_used}.")
                    answer_success=True
                
                if answer_success==True:
                    active_model=chosen_model4
                    break    
            except Exception as e:
                print(F"Model {chosen_model4} failed at the task ({e}).Retrying with another model.")   
                answer_fallback.remove(chosen_model4)
    if not answer_success:
        print(F"""ALL MODELS FAILED. 
        PLEASE CHECK YOUR API KEYS AND ENSURE THAT YOU HAVE NOT EXHAUSTED YOUR LIMITS.
        TRY USING ANOTHER PROVIDER.""")    
        break

    if history_points>=6:
        summary_success=False
        summary_fallback=list(global_fallback)
        while True:
            try:
                chosen_summary_model=random.choice(summary_fallback)
                summary_llm= ChatOpenAI(
                    model=chosen_summary_model,
                    base_url=chosen_base_url,
                    api_key=chosen_api_key
                )

                summary=summary_llm.invoke(
                    [("system","Summarize the conversation so far. Split the summary into two clear sections: user questions and AI responses.")]+conversation_history
                )
                summary_data=summary.content
                summarised_data.append(summary_data)
                conversation_history=[("assistant", f"Summary of previous context is {summary_data}")]
                history_points=1  
                summary_success=True
            except:
                summary_fallback.remove(chosen_summary_model)    
 
            if not summary_fallback:
                print("WARNING: All fallback models failed to summarize. Continuing with full context.")    
                summary_success=True
                break
            if summary_success==True:
                break             
