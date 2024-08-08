import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import pandas as pd

class AzureSearchClient:
    def __init__(self):
        load_dotenv()
        service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        key = os.getenv("AZURE_SEARCH_API_KEY")
        self.client = SearchClient(
            service_endpoint, index_name, AzureKeyCredential(key)
        )
    
    def number_of_docs(self):
        doc_count = self.client.get_document_count()
        return doc_count

    def search_with_json(self, **kwargs):
        results = self.client.search(**kwargs)
        return results
    
    def facet_search(self, **kwargs):
        results = self.client.search(**kwargs)
        return results.get_facets()

    def search(self, search_text):
        results = self.client.search(
            query_type="semantic",
            minimum_coverage=80,
            search_text=search_text,
            include_total_count=True,
            semantic_configuration_name=os.getenv("AZURE_SEARCH_SEMANTIC_CONFIG_NAME"),
        )

        df = pd.DataFrame(list(results))

        if df.empty:
            return "No data found."
        else:
            filtered_results = df[df["@search.score"] > 30]        
            filtered_results['json'] = filtered_results.apply(lambda x: x.to_json(), axis=1)
            return filtered_results['json'].to_list()