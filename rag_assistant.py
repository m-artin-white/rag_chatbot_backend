import yaml
import logging
import os
import json
import re
from clients.az_oai_client import AzureOpenAIClient
from clients.az_search_client import AzureSearchClient
from clients.cosmos_client import CosmosDBClient
from function_call_tools.function_defs import *


class RAGAssistant:
    def __init__(
        self, vector_db_client: AzureSearchClient, az_oai_client: AzureOpenAIClient, cosmos_client: CosmosDBClient
    ):
        self.vector_db_client = vector_db_client
        self.az_oai_client = az_oai_client
        self.cosmos_client = cosmos_client

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompts_file_path = os.path.join(base_dir, "prompts", "prompts.yaml")

    def _get_prompt(self, prompt_name):
        try:
            with open(self.prompts_file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)[prompt_name]
        except FileNotFoundError:
            raise Exception("Prompt file not found.")
        except yaml.YAMLError:
            raise Exception("Error parsing the YAML file.")

    def _get_documents(self, query: str):
        try:
            search_results = self.vector_db_client.search(search_text=query)
        except Exception as e:
            logging.error(f"Failed to query vector database: {e}")
            return "Error querying vector database"
        return search_results

    def rename_key(self, json_obj, old_key, new_key):
        if old_key in json_obj:
            json_obj[new_key] = json_obj.pop(old_key)
        return json_obj

    def generate_response(self, query: str):

        prompt_function_call = self._get_prompt(prompt_name="prompt_function_call")

        messages_function_call = [
            {"role": "system", "content": prompt_function_call},
            {"role": "user", "content": query},
        ]

        response = self.az_oai_client.generate_completion(
            messages=messages_function_call, tools=functions
        )
        
        query_type = response.tool_calls[0].function.name

        messages = [
                {"role": "system", "content": "{prompt}"},
                {"role": "user", "content": "{query}"},
            ]

        if query_type == "_get_documents":
            try:
                documents = self._get_documents(query)
                concatenated_json = "\n".join([json.dumps(document) for document in documents])
            except Exception as e:
                logging.error(
                    f"Failed to retrieve documents from vector database for query '{query}': {e}"
                )
                return "Failed to retrieve document data."

            prompt = f"{self._get_prompt(prompt_name='prompt_get_documents')}\n\n{concatenated_json}"
            messages[0]["content"] = messages[0]["content"].format(prompt=prompt)
            messages[1]["content"] = messages[1]["content"].format(query=query)

            try:
                response = self.az_oai_client.generate_completion(
                    messages=messages, tools=None
                )
            except Exception as e:
                logging.error(f"AI model completion generation failed: {e}")
                return "Failed to generate completion from AI model."

            return response.content
        
        # This section below is only functional if you provide a detailed description of the dataset in the prompt.yaml file 
        # under the prompt_dataset key.
        elif query_type == "_answer_on_dataset":

            prompt = self._get_prompt(prompt_name="prompt_facets")
            messages[0]["content"] = messages[0]["content"].format(prompt=prompt)
            messages[1]["content"] = messages[1]["content"].format(query=query)

            try:
                response = self.az_oai_client.generate_completion(
                    messages=messages, response_format={ "type": "json_object" }
                )
    
                json_response = json.loads(response.content)

                json_response = self.rename_key(json_response, "search", "search_text")
                json_response['query_type'] = "full"
                json_response['search_mode'] = "all"
                
                facet_response = self.vector_db_client.facet_search(**json_response)
            except Exception as e:
                logging.error(f"AI model completion generation failed: {e}")
                return "Failed to generate completion from AI model."
            
            prompt = f"{self._get_prompt(prompt_name='prompt_dataset')}\n\n{json.dumps(facet_response)}"

            messages = [
                {"role": "system", "content": "{prompt}"},
                {"role": "user", "content": query},
            ]

            messages[0]["content"] = messages[0]["content"].format(prompt=prompt)
            messages[1]["content"] = messages[1]["content"].format(query=query)

            try:
                response = self.az_oai_client.generate_completion(
                    messages=messages, tools=None
                )
            
                return response.content
                
            except Exception as e:
                logging.error(f"AI model completion generation failed: {e}")
                return "Failed to generate completion from AI model."

        else:
            prompt_general = self._get_prompt(prompt_name="prompt_general")

            messages[0]["content"] = messages[0]["content"].format(prompt=prompt_general)
            messages[1]["content"] = messages[1]["content"].format(query=query)

            response = self.az_oai_client.generate_completion(
                messages=messages, tools=None
            )

            return response.content