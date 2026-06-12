from google.genai import types
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_case import EvalCase, Invocation, IntermediateData

invocation = Invocation(
    invocation_id="weather_tokyo_1",
    user_content=types.Content(role="user", parts=[types.Part(text="What's the weather in Tokyo?")]),
    final_response=types.Content(role="model", parts=[types.Part(text="The weather in Tokyo is clear, 28 °C.")]),
    intermediate_data=IntermediateData(
        tool_uses=[types.FunctionCall(name="get_weather", args={"city": "Tokyo"})]
    ),
)
eval_set = EvalSet(
    eval_set_id="weather_basics",
    name="weather basics",
    eval_cases=[EvalCase(eval_id="weather_tokyo", conversation=[invocation])],
)
