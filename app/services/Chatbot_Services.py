import os
import re
import inspect
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from spellchecker import SpellChecker
from langchain_google_genai import ChatGoogleGenerativeAI
from app.embeddings import db
from langchain.agents import Tool
from app.services.SSH_Services import run_command, ssh_sessions
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from collections import deque
from langchain.agents import initialize_agent, AgentType, Tool

history = deque(maxlen=5) 
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    transport="rest"
)

spell = SpellChecker()

_sonic_vocab_loaded = False
def load_sonic_vocab():
    global _sonic_vocab_loaded
    if _sonic_vocab_loaded:
        return

    try:
        sonic_vocab = set()
        sample_docs = db.similarity_search("sonic", k=20)  # smaller for speed
        for doc in sample_docs:
            if not getattr(doc, "page_content", None):
                continue
            for word in doc.page_content.split():
                sonic_vocab.add(word.lower())

        if sonic_vocab:
            spell.word_frequency.load_words(list(sonic_vocab))
            print(f"✅ Loaded {len(sonic_vocab)} SONiC-specific words into spellchecker")

        _sonic_vocab_loaded = True
    except Exception as e:
        print("⚠️ Could not build SONiC vocabulary:", e)


# ✅ Define critical SONiC terms
SONIC_TERMS = {"vlans", "vlan", "interface", "interfaces", "port", "ports", "sonic", "routing"}

# ✅ Add them with high frequency so spellchecker prefers them
for term in SONIC_TERMS:
    spell.word_frequency.add(term, 10000)  # artificially boost frequency


def correct_spelling(text: str) -> str:
    words = text.split()
    corrected_sentence = []
    for word in words:
        lw = word.lower()

        # ✅ Always trust SONiC terms
        if lw in SONIC_TERMS:
            corrected_sentence.append(word)
            continue

        # ✅ If it's close to a SONiC term, force it
        candidates = spell.candidates(word)
        sonic_candidates = [c for c in candidates if c in SONIC_TERMS]
        if sonic_candidates:
            corrected_sentence.append(sonic_candidates[0])
            continue

        # ✅ Otherwise, normal correction
        correction = spell.correction(word)
        corrected_sentence.append(correction if correction else word)

    return " ".join(corrected_sentence)



def preprocess_input(text: str):
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = correct_spelling(text)
    return text



prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant for Sonic Switch with access to toolsFollow this format:

If the user asks about a command or has an unclear query, always firstly use `search_sonic` to look it up before executing any command with execute_command tool.
If the user provides a valid CLI command or asks you to execute one, run it with `execute_command` type in it the command exactly as returned from the sonic documentation with no additions and return the output if there is one.
if the user asks what is the command for something return it with no additions unless the command needs specific args you can specify them and don't execute it unless his query asks you to after you understand what command he wants by using search_sonic tool.
if the command can't be executed for some reason return it, or if you don't know the reason it failed search the sonic for what the command needs for it to succeed maybe the user needs to send additional info ask him to provide you with it.
You must NEVER write `OBSERVATION:` yourself.
Only the system (outside you) will fill that in.
Do not write OBSERVATION or FINAL yet.
if user asks for multiple actions, execute them sequentially, with its own THOUGHT/ACTION/INPUT/OBSERVATION/FINAL
if multiple actions don't fill the FINAL yet until all actions are done

Never include OBSERVATION or THOUGHT inside the INPUT block. 
The INPUT must contain only the exact CLI command with no extra text. 
                                        
Available tools:
- search_sonic: Search SONiC documentation for relevant info.
- execute_command: Run SONiC CLI commands if user asks you to execute them only via SSH. Input should be a valid SONiC CLI command.

please return only the final answer                                   
THOUGHT: your reasoning
ACTION: the tool to use (if needed)
INPUT: the input for the tool
OBSERVATION: (this will be filled in later by the system, do NOT write this yourself)
FINAL:  the final answer to the user
This is your scratchpad of reasoning and user input so far: {input}
here is the conversation history so far: {conv_history}
""")

chain = prompt | llm | StrOutputParser()

def search_sonic(query: str) -> str:
    """
    Search SONiC documentation for relevant info.
    Input: user query (string).
    Output: top matching result as a string.
    """
    results = db.similarity_search(query, k = 3)
    context = "\n\n".join([doc.page_content for doc in results])
    print("context in search docs: \n" ,context)
    return context


def make_run_command_tool(conn):
    async def run_with_conn(command: str) -> str:
        result = await run_command(conn, command)
        return result
    return run_with_conn



async def invoke_tool(tool_func, tool_input):
    if inspect.iscoroutinefunction(tool_func):
        return await tool_func(tool_input)
    else:
        return tool_func(tool_input)



async def chatbot_service(websocket: WebSocket, username: str):
    await websocket.accept()
    conn = ssh_sessions.get(username)
    if not conn:
        await websocket.send_json({"No active SSH session"})
        await websocket.close()
        return
    
    execute_command = make_run_command_tool(conn)
    
    tools = [
        Tool(
            name="execute_command",
            func=execute_command,   
            # coroutine=execute_command,  # async version
            description="Run SONiC CLI commands via SSH..."
        ),
        Tool(
        name="search_sonic",
        func=search_sonic,
        description="Search the SONiC documentation or database for the best matching command when the query is unclear."
        )
    ]
    # agent = initialize_agent(
    #     tools=tools,
    #     llm=llm,
    #     agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # handles ACTION/OBSERVATION loops
    #     verbose=True
    # )
    tool_map = {t.name: t.func for t in tools}

    # async def run_agent(user_input: str, conv_history: str,max_steps: int = 5):
    #     context = f"User asked: {user_input}"
    #     # response = chain.invoke({"input": context, "conv_history": conv_history})
    #     for step in range(max_steps):

    #         response = chain.invoke({"input": context, "conv_history": conv_history})

    #         print(f"\n=== Step {step+1} ===\n{response}\n")

    #         if "FINAL:" in response and "ACTION:" not in response:
    #                 return response.split("FINAL:", 1)[1].strip()

    #         if "ACTION:" in response and "INPUT:" in response:
    #             lines = response.splitlines()
    #             action_line = next((line for line in lines if line.startswith("ACTION:")), None)
    #             input_line = next((line for line in lines if line.startswith("INPUT:")), None)


    #             tool_name = action_line.split(":", 1)[1].strip() if action_line else None
    #             tool_input = input_line.split(":", 1)[1].strip() if input_line else None


    #             if tool_name in tool_map:
    #                 print(f"Invoking tool: {tool_name} with input: {tool_input}")

    #                 result = await invoke_tool(tool_map[tool_name], tool_input)
    #                 print("result", result)
    #                 context += f"\nACTION: {tool_name}\nINPUT: {tool_input}\nOBSERVATION: {result}"
    #             else:
    #                 context += f"\nOBSERVATION: Unknown tool {tool_name}"
        
    #         else:
    #             print("Agent stopped early")
    #             return response.strip()
    #         # response = chain.invoke({"input": context, "conv_history": ""})
    #     return "Reached max steps without final answer."

    async def run_agent(user_input: str, history: deque, max_steps: int = 5):

        conv_history = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in list(history)
        ])

        context = f"User asked: {user_input}"
        for step in range(max_steps):
            response = chain.invoke({"input": context, "conv_history": conv_history})
            print(f"\n=== Step {step+1} ===\n{response}\n")

            if "FINAL:" in response:
                
                final_answer = response.split("FINAL:", 1)[1].strip()
                actions = re.findall(
                    r"ACTION:\s*(\w+)\s*INPUT:\s*([\s\S]*?)(?=(?:ACTION:|FINAL:|$))",
                    response
                )

                if actions:
                    for tool_name, tool_input in actions:
                        tool_name = tool_name.strip()
                        tool_input = tool_input.strip()
                        if tool_name in tool_map:
                            print(f"Invoking tool: {tool_name} with input: {tool_input}")
                            result = await invoke_tool(tool_map[tool_name], tool_input)
                            print("result:" , result)
                            context += f"\nACTION: {tool_name}\nINPUT: {tool_input}\nOBSERVATION: {result}"
                        else:
                            context += f"\nOBSERVATION: Unknown tool {tool_name}"
                else:
                    print("⚠️ No ACTION/INPUT blocks found in response")

                return final_answer

            elif "ACTION:" in response and "INPUT:" in response:
                # handle normal single action case
                actions = re.findall(
                    r"ACTION:\s*(\w+)\s*INPUT:\s*([\s\S]*?)(?=(?:ACTION:|FINAL:|$))",
                    response
                )

                if actions:
                    for tool_name, tool_input in actions:
                        tool_name = tool_name.strip()
                        tool_input = tool_input.strip()

                        if tool_name in tool_map:
                            print(f"Invoking tool: {tool_name} with input: {tool_input}")
                            result = await invoke_tool(tool_map[tool_name], tool_input)
                            print("result:" , result)
                            context += f"\nACTION: {tool_name}\nINPUT: {tool_input}\nOBSERVATION: {result}"
                        else:
                            context += f"\nOBSERVATION: Unknown tool {tool_name}"
                else:
                    print("⚠️ No ACTION/INPUT blocks found in response")
        
            else:
                return response.strip()

        return "Reached max steps without final answer."

    try:
        while True:
            user_input = await websocket.receive_text()

            load_sonic_vocab()

            clean_input = preprocess_input(user_input)

            history.append({"role": "user", "content": clean_input})
            response = await run_agent(clean_input,history)
            # response = await agent.arun(clean_input)
            history.append({"role": "assistant", "content": response})
            
            await websocket.send_text(response)

    except WebSocketDisconnect:
        print("Client disconnected, stopping...")

    except Exception as e:
        print("⚠️ Chatbot crashed with error:", e)
        await websocket.close()
