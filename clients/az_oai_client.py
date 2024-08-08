import os
from dotenv import load_dotenv
from openai import AzureOpenAI

class AzureOpenAIClient:
    def __init__(self):
        load_dotenv()
        self.az_client = AzureOpenAI(
            azure_endpoint = os.getenv('AZURE_OPEN_AI_ENDPOINT'), 
            api_key = os.getenv('AZURE_OPEN_AI_KEY'),  
            api_version = os.getenv('AZURE_OPEN_AI_VERSION')
        )

    def generate_completion(
        self,
        messages: list[dict],
        tools: list | None = None,
        max_tokens: int | None = None,
        temperature: int = 0,
        model: str = os.getenv('AZURE_OPEN_AI_MODEL'),
        response_format: dict | None = None,
    ):
        try:
            response_message = self.az_client.chat.completions.create(
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model,
                response_format=response_format,
            )
        except Exception as e:
            return str(e)
        else:
            return response_message.choices[0].message