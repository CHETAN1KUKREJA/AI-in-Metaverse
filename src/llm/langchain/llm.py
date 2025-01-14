from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_json_chat_agent, AgentExecutor

from input_prompt import prompt_example, human, system
from tools import *


class LLM:
    def __init__(self):
        # prevent load unnecessary model
        from backend.langchain.custom_llm_mistral import llm_mistral
        # from backend.langchain.custom_llm_qwen import llm_qwen
        
        self.prompt_system = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", human),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        self.tools = [goto, talk, trade, eat, collect_apples]
        self.tools_to_end = ["talk", "trade", "goto", "collect_apples"]
        self.tools_all = ["talk", "trade", "goto", "eat", "collect_apples"]

        self.agent = create_json_chat_agent(tools=self.tools, llm=llm_mistral, prompt=self.prompt_system, stop_sequence=["STOP"], template_tool_response="{observation}")

        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True)

    def update_memory(self, call_batch):
        # TODO: use the real memory update
        pass
    
        # call = call_batch[0]
        # match call["name"]:
        #     case "go_to":
        #         # mem = f"You go to {call['arguments']['location']}, the reason is: {call['arguments']['explanation_for_this_action_and_arguments']}"
        #         mem = f"You go to {call['arguments']['location']}."
        #         self.memory.append(mem)
        #     case "enter":
        #         mem = f"You enter {call['arguments']['location']}."
        #         self.memory.append(mem)
        #     case "talk":
        #         mem = f"You try to talk with \"{call['arguments']['other_agent']}\". But \"{call['arguments']['other_agent']}\" doesn't exist here!"
        #         self.memory.append(mem)
        #     case "exit":
        #         mem = f"You exit. Now you are outside again."
        #         self.memory.append(mem)

    def iterate_step(self, input_jsons):
        call_batch = []
        for input_json in input_jsons:
            Json_output_calls = []
            
            # TODO: use the real prompt
            prompt = input_json
            
            for step in self.agent_executor.stream({"input": prompt}):
                print(step)
                if step["actions"][0].tool not in self.tools_all:
                    print("hallucination")
                    break
                curr_step = {}
                curr_step["action"] = step["actions"][0].tool
                curr_step["action_input"] = step["actions"][0].tool_input
                Json_output_calls.append(curr_step)
                if step["actions"][0].tool in self.tools_to_end:
                    break
            
            call_batch.append(Json_output_calls)
            
        return call_batch
