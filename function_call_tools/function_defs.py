functions = [
        {
        "type": "function",
        "function": {
            "name": "_get_documents",
            "description": "Use to get documents from the vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "_answer_on_dataset",
            "description": "Use to answer questions on all documents stored in the vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "_general_function",
            "description": "Use to answer questions on general topics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
]