from langchain.tools import StructuredTool


def tool_error_builder(error_msg, name="error_tool"):
    """Creates a placeholder tool that returns an error message."""
    return StructuredTool.from_function(
        name=name,
        func=lambda: error_msg,
        description=f"""Returns a placeholder tool indicating an error.
        {error_msg[:20]}...
        IF THIS TOOL EXISTS, PLEASE USE THIS TOOL IMMEDIATELY TO NOTIFY THE USER.
        SHOW FULL ERROR LOG.
        """)
