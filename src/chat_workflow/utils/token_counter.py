from typing import List, Callable

from transformers import AutoTokenizer
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)


def str_token_counter(text: str, tokenizer) -> int:
    tokens = tokenizer.tokenize(text)
    return len(tokens)


def msg_token_counter_factory(model_name: str) -> Callable[[List[BaseMessage]], int]:
    def msg_token_counter(messages: List[BaseMessage]) -> int:
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        num_tokens = 3  # every reply is primed with <|start|>assistant<|message|>
        tokens_per_message = 3
        tokens_per_name = 1

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, ToolMessage):
                role = "tool"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                raise ValueError(f"Unsupported message type {msg.__class__}")

            num_tokens += (
                tokens_per_message +
                str_token_counter(role, tokenizer) +
                str_token_counter(msg.content, tokenizer)
            )

            if msg.name:
                num_tokens += tokens_per_name + str_token_counter(msg.name, tokenizer)

        return num_tokens

    return msg_token_counter
