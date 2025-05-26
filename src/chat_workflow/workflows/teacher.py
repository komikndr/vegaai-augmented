import os
import re
import base64
import mimetypes
import json
from datetime import datetime
import pandas as pd

from sqlalchemy import create_engine, text

import chainlit as cl
from chainlit.input_widget import Select
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.prebuilt import ToolNode

from .base import BaseWorkflow, BaseState
from ..llm import llm_factory, ModelCapability

from ..utils.token_counter import msg_token_counter_factory

from ..tools.postgre_db import get_postgre_sql_toolkit
from ..tools.plot_composite import plot_composite_figure


def get_postgre_engine():
    postgre_host = os.getenv("POSTGRE_DS_HOST")
    postgre_port = os.getenv("POSTGRE_DS_PORT")
    postgre_username = os.getenv("POSTGRE_DS_USERNAME")
    postgre_password = os.getenv("POSTGRE_DS_PASSWORD")
    postgre_db = os.getenv("POSTGRE_DS_DB")

    postgre_conn = f"postgresql://{postgre_username}:{postgre_password}@{postgre_host}:{postgre_port}/{postgre_db}"
    engine = create_engine(
        postgre_conn, connect_args={"connect_timeout": 1}, pool_pre_ping=True
    )
    return engine


def dump_to_postgres(engine, question_text):
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO questionsheet (timestamp, question) VALUES (:ts, :q)"
                ),
                {"ts": datetime.utcnow(), "q": json.dumps({"text": question_text})},
            )
    except Exception as e:
        print(f"⚠️ Failed to insert into DB: {e}")


class GraphState(BaseState):
    chat_model: str


class TeacherChat(BaseWorkflow):
    def __init__(self):
        super().__init__()

        self.capabilities = {ModelCapability.TEXT_TO_TEXT, ModelCapability.TOOL_CALLING}
        self.tools = [plot_composite_figure] + get_postgre_sql_toolkit()
        self.engine = get_postgre_engine()

    def create_graph(self) -> StateGraph:
        graph = StateGraph(GraphState)
        graph.add_node("chat", self.chat_node)
        graph.add_node("tools", ToolNode(self.tools))

        graph.set_entry_point("chat")
        graph.add_conditional_edges("chat", self.tool_routing)
        graph.add_edge("tools", "chat")
        return graph

    async def chat_node(self, state: GraphState, config: RunnableConfig) -> GraphState:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a multimodal assistant that speaks in Bahasa Indonesia. You are an agent designed to help '
                    teachers upload and manage question sheets in a PostgreSQL database. You will receive question
                    files in various formats (.txt, .csv, .xlsx), show a preview of their content, the content will automatically
                    inserted into database, check if the content already exist in db . You can also help teachers query
                    the stored questions using syntactically correct PostgreSQL queries, limiting results to at most 5 entries. \n
                    Do not perform DML operations (INSERT, UPDATE, DELETE, DROP) directly except when saving
                    uploaded question files. You may use Temporary Views for intermediate data if needed.
                    \n
                    If there is any tool with errors, immediately inform the teacher clearly.
                    \n
                    Only retrieve relevant columns based on the teacher’s question.
                    \n
                    Use only information from available tools to answer.
                    Respond always in Bahasa Indonesia.
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        llm = llm_factory.create_model(
            self.output_chat_model, model=state["chat_model"], tools=self.tools
        )

        if state["chat_model"].startswith("(openai)"):
            trimmer = trim_messages(
                token_counter=llm,
                strategy="last",
                max_tokens=32000,
                start_on="human",
                end_on=("human", "tool"),
                include_system=True,
            )
            chain: Runnable = prompt | trimmer | llm
            return {"messages": [await chain.ainvoke(state, config=config)]}

        else:
            model_name = re.sub(r"^\([^)]*\)", "", state["chat_model"]).removesuffix(
                ":latest"
            )
            token_count = msg_token_counter_factory(model_name)
            trimmer = trim_messages(
                token_counter=token_count,
                strategy="last",
                max_tokens=32000,
                start_on="human",
                end_on=("human", "tool"),
                include_system=True,
            )
            chain: Runnable = prompt | trimmer | llm
            return {"messages": [await chain.ainvoke(state, config=config)]}

    def create_default_state(self) -> GraphState:
        return {
            "name": self.name(),
            "messages": [],
            "chat_model": "",
        }

    @classmethod
    def name(cls) -> str:
        return "TEACHER CHAT"

    @property
    def output_chat_model(self) -> str:
        return "chat_model"

    @classmethod
    def chat_profile(cls) -> cl.ChatProfile:
        return cl.ChatProfile(
            name=cls.name(),
            markdown_description="Teacher chat",
            icon="/public/favicon.png",
            default=True,
            starters=[
                cl.Starter(
                    label="Check Available Table in Database",
                    message="Please show available table in database",
                    # icon="https://cdn1.iconfinder.com/data/icons/photography-calendar-speaker-person-thinking-3d-il/128/13.png",
                ),
            ],
        )

    @property
    def chat_settings(self) -> cl.ChatSettings:
        return cl.ChatSettings(
            [
                Select(
                    id="chat_model",
                    label="Chat Model",
                    values=sorted(
                        llm_factory.list_models(capabilities=self.capabilities)
                    ),
                    initial_index=0,
                ),
            ]
        )

    def format_message(self, msg: cl.Message) -> HumanMessage:
        if not msg.elements:
            return HumanMessage(content=msg.content)

        formatted_content = [{"type": "text", "text": msg.content}]

        for element in msg.elements:
            mime = element.mime or mimetypes.guess_type(element.path)[0] or ""

            if "image" in mime:
                with open(element.path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    formatted_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        }
                    )

            elif mime in [
                "text/csv",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ]:
                try:
                    df = (
                        pd.read_csv(element.path)
                        if element.path.endswith(".csv")
                        else pd.read_excel(element.path)
                    )
                    head_str = df.head().to_string(index=False)
                    preview = f"Here is a preview of the uploaded csv file:\n{head_str}"
                    formatted_content.append({"type": "text", "text": preview})
                    dump_to_postgres(self.engine, head_str)
                except Exception as e:
                    error_msg = f"⚠️ Failed to read uploaded file {element.path}: {e}"
                    formatted_content.append({"type": "text", "text": error_msg})

            elif mime == "text/plain":
                try:
                    with open(element.path, "r", encoding="utf-8") as f:
                        text_content = f.read()
                    preview_text = text_content[:1000]
                    preview = (
                        f"Here is a preview of the uploaded text file:\n{preview_text}"
                    )
                    formatted_content.append({"type": "text", "text": preview})
                    dump_to_postgres(self.engine, text_content)
                except Exception as e:
                    error_msg = (
                        f"⚠️ Failed to read uploaded text file {element.path}: {e}"
                    )
                    formatted_content.append({"type": "text", "text": error_msg})

        return HumanMessage(content=formatted_content)
