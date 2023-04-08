from flask import Flask, render_template, request, jsonify
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import LLMChain, SerpAPIWrapper, LLMMathChain
from langchain.utilities import PythonREPL, BashProcess, WikipediaAPIWrapper
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.chat_models import ChatOpenAI
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, HumanMessage
import re
import os
import openai

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
google_cse_id = os.environ.get("GOOGLE_CSE_ID")
google_api_key = os.environ.get("GOOGLE_API_KEY")
serpapi_api_key = os.environ.get("SERPAPI_API_KEY")
wolfram_alpha_appid = os.environ.get("WOLFRAM_ALPHA_APPID")

search_serp = SerpAPIWrapper()
wolfram = WolframAlphaAPIWrapper()
python_repl = PythonREPL()
#llm_math_chain = LLMMathChain()
bash = BashProcess()
#requests = TextRequestsWrapper()
wikipedia = WikipediaAPIWrapper()
#search_google = GoogleSearchAPIWrapper()

tools = [
  Tool(name="SearchSerp",
       func=search_serp.run,
       description=
       "useful for when you need to answer questions about current events"),
  Tool(name="WolframAlpha",
       func=wolfram.run,
       description=
       "useful for when you need to answer questions using Wolfram Alpha API"),
  Tool(
    name="PythonREPL",
    func=python_repl.run,
    description=
    "useful for when you need to perform complex calculations using Python code"
  ),
#  Tool(name="Calculator",
#       func=llm_math_chain.run,
#       description="useful for when you need to answer questions about math"),
  Tool(
    name="Bash",
    func=bash.run,
    description="useful for when you need to interact with local file system"),
#  Tool(
#    name="Requests",
#    func=requests.run,
#    description=
#    "useful for when you need to get information you do not have access to by fetching data from a url"
#  ),
  Tool(
    name="Wikipedia",
    func=wikipedia.run,
    description="useful for when you need to get information using wikipedia")
]

template = """You are a helpful assistant that answer's as best as you can on the following topic:

{input}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer

Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""


class CustomPromptTemplate(BaseChatPromptTemplate):
  template: str
  tools: List[Tool]

  def format_messages(self, **kwargs) -> str:
    intermediate_steps = kwargs.pop("intermediate_steps")
    thoughts = ""
    for action, observation in intermediate_steps:
      thoughts += action.log
      thoughts += f"\nObservation: {observation}\nThought: "
    kwargs["agent_scratchpad"] = thoughts
    kwargs["tools"] = "\n".join(
      [f"{tool.name}: {tool.description}" for tool in self.tools])
    kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
    formatted = self.template.format(**kwargs)
    return [HumanMessage(content=formatted)]


prompt = CustomPromptTemplate(template=template,
                              tools=tools,
                              input_variables=["input", "intermediate_steps"])


class CustomOutputParser(AgentOutputParser):

  def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
    if "Final Answer:" in llm_output:
      return AgentFinish(
        return_values={
          "output": llm_output.split("Final Answer:")[-1].strip()
        },
        log=llm_output,
      )
    regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
    match = re.search(regex, llm_output, re.DOTALL)
    if not match:
      return AgentFinish(
        return_values={"output": llm_output.strip()},
        log=llm_output,
      )

    action = match.group(1).strip()
    action_input = match.group(2)
    return AgentAction(tool=action,
                       tool_input=action_input.strip(" ").strip('"'),
                       log=llm_output)


output_parser = CustomOutputParser()

llm = ChatOpenAI(temperature=0)

llm_chain = LLMChain(llm=llm, prompt=prompt)
tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(llm_chain=llm_chain,
                             output_parser=output_parser,
                             stop=["\nObservation:"],
                             allowed_tools=tool_names)

# Run the agent
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                    tools=tools,
                                                    verbose=True)


@app.route("/")
def home():
  return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
  user_input = request.form["userInput"]
  result = agent_executor.run(user_input)
  return jsonify(result=result)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080)
