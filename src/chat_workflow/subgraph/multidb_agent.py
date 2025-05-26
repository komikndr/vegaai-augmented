from typing import Annotated, Literal, Optional

from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda

from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph, START

from langgraph.prebuilt import tools_condition
from langchain_core.tools import tool
from typing import Callable

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from .base import BaseWorkflow, BaseState
from ..llm import llm_factory, ModelCapability


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class GraphState(BaseState):
    chat_model: str
    dialog_state: Annotated[
        list[
            Literal[
                "assistant",
                "weather",
                "place",
            ]
        ],
        update_dialog_stack,
    ]









async def weather_chat_node(
    self, state: GraphState, config: RunnableConfig
) -> GraphState:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="""
                System: You are a specialized assistant for handling weather and atmospheric conditions.\n
                The primary assistant delegates work to you whenever the user needs help checking the weather conditions.\n
                Confirm the status of the weather with the customer.\n
                If you need more information or the customer changes their mind, escalate the task back to the main assistant.\n
                If the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog
                to the host assistant. Do not waste the user’s time. Do not make up invalid tools or functions.
            """
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    llm = llm_factory.create_model(
        self.output_chat_model,
        model=state["chat_model"],
        tools=[get_humidty, get_weather, CompleteOrEscalate],
    )
    chain: Runnable = prompt | llm
    return {"messages": [await chain.ainvoke(state, config=config)]}


async def place_chat_node(
    self, state: GraphState, config: RunnableConfig
) -> GraphState:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="""
                System: You are a specialized assistant for handling the possible places that users want to visit.\n
                The primary assistant delegates work to you whenever the user needs help finding the best place to visit.\n
                Confirm the status of the place with the customer.\n
                If you need more information or the customer changes their mind, escalate the task back to the main assistant.\n
                If the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog
                to the host assistant. Do not waste the user’s time. Do not make up invalid tools or functions.
            """
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    llm = llm_factory.create_model(
        self.output_chat_model,
        model=state["chat_model"],
        tools=[get_vacation_place, CompleteOrEscalate],
    )

    chain: Runnable = prompt | llm
    return {"messages": [await chain.ainvoke(state, config=config)]}


# Primary Assistant


class ToWeatherAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle weather conditions."""

    location: str = Field(
        description="The location where the user wants to check the weather condition"
    )
    request: str = Field(description="Any addtional  questions about the weather.")

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Bandung",
                "request": "What is the weather in bandung.",
            }
        }


class ToPlaceAssistant(BaseModel):
    """Transfers work to a specialized assistant to place tourist."""

    request: str = Field(description="Any addtional  questions about the places.")



builder = StateGraph(GraphState)
builder.set_entry_point("primary_assistant")


builder.add_node(
    "enter_weather_check",
    create_entry_node("Weather Assistant", "update_weather"),
)
builder.add_node("update_weather", weather_chat_node)
builder.add_edge("enter_weather_check", "update_weather")
builder.add_node(
    "update_weather_safe_tools",
    create_tool_node_with_fallback(update_weather_safe_tools),
)

builder.add_edge("update_weather_safe_tools", "update_weather")
builder.add_conditional_edges(
    "update_weather",
    route_update_weather,
    ["update_weather_safe_tools", "leave_skill", END],
)
builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")
builder.add_node("primary_assistant", Assistant(assistant_runnable))
builder.add_node(
    "primary_assistant_tools", create_tool_node_with_fallback(primary_assistant_tools)
)

builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    [
        "enter_weather_check",
        "primary_assistant_tools",
        END,
    ],
)
builder.add_edge("primary_assistant_tools", "primary_assistant")
builder.add_conditional_edges("fetch_user_info", route_to_workflow)

part_4_graph = builder.compile()
