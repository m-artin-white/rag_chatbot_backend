import os
import json
import uuid
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions
from concurrent.futures import ThreadPoolExecutor, as_completed

class CosmosDBClient:
    def __init__(self):
        load_dotenv()
        self.client = CosmosClient(
            url=os.getenv("COSMOS_URL"), credential=os.getenv("COSMOS_KEY")
        )
        self.db_name = os.getenv("COSMOS_DB_NAME")
        self.container_name = os.getenv("COSMOS_DB_CONTAINER_NAME")
        self.database = self.client.get_database_client(self.db_name)
        self.container = self.database.get_container_client(self.container_name)

    def generate_unique_id(self) -> str:
        unique_id = uuid.uuid4()
        return str(unique_id)

    def query_cosmos(self, ids: list) -> list:
        id_list = ", ".join(f"'{id}'" for id in ids)
        query = f"SELECT * FROM c WHERE c.number IN ({id_list})"
        items = list(
            self.container.query_items(query=query, enable_cross_partition_query=True)
        )
        return items

    def upsert_cosmos_parallel(self, file_path: str):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        count = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.upsert_item, item) for item in data]
            for future in futures:
                future.result()
                count += 1

        print("Total items upserted:", count)

    def upsert_item(self, item):
        try:
            item["id"] = self.generate_unique_id()
            response = self.container.upsert_item(item)
            print("Upserted item:", response["id"])
        except exceptions.CosmosHttpResponseError as e:
            print(f'Error upserting item {item.get("id", "Unknown ID")}: {e}')
        except Exception as e:
            print(
                f'An unexpected error occurred for item {item.get("id", "Unknown ID")}: {str(e)}'
            )

    def delete_all_items(self):
        def delete_item(item):
            try:
                self.container.delete_item(item, partition_key=item['id'])
                return f"Deleted item with id: {item['id']}"
            except exceptions.CosmosHttpResponseError as e:
                return f"Error deleting item {item['id']}: {e}"
            except Exception as e:
                return f"Unexpected error deleting item {item['id']}: {str(e)}"

        try:
            items = list(self.container.read_all_items())
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_item, item) for item in items]
                for future in as_completed(futures):
                    print(future.result())
            print("All items processed.")
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error reading items: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")


    def execute_cosmos_db_query(self, query: str) -> list:
        try: 
            items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            results = []
            for item in items:
                results.append(item)
            return results
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error querying items: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")