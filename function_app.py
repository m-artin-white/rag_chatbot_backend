import azure.functions as func
import logging
import json
from clients.az_oai_client import AzureOpenAIClient
from clients.az_search_client import AzureSearchClient
from clients.cosmos_client import CosmosDBClient
from rag_assistant import RAGAssistant

app = func.FunctionApp()

vector_db_client = AzureSearchClient()
az_oai_client = AzureOpenAIClient()
cosmos_client = CosmosDBClient()

rag_assistant = RAGAssistant(
    vector_db_client=vector_db_client,
    az_oai_client=az_oai_client,
    cosmos_client=cosmos_client,
)

@app.route(route="query", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
async def query(req: func.HttpRequest) -> func.HttpResponse:
    try:
        query = req.params.get("query")
        response = rag_assistant.generate_response(query=query)
        logging.info(response)

        response_body = {"response": response}
        return func.HttpResponse(
            body=json.dumps(response_body),
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST",  # Corrected
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
        )

    except ValueError as ve:
        logging.error(f"Validation error: {ve}", exc_info=True)
        return func.HttpResponse(f"Validation error: {ve}", status_code=400)

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(f"Bad request. {e}", status_code=400)