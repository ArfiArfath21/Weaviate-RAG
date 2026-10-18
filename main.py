import json
import os

import weaviate
from weaviate.classes.config import Configure
from weaviate.classes.query import MetadataQuery


client = weaviate.connect_to_local()
print(client.is_ready())  # Should print: `True`

vectorizer_config = Configure.Vectorizer.text2vec_ollama(  # Configure the Ollama embedding integration
    api_endpoint="http://host.docker.internal:11434",
    model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),  # The model to use
)

# generative_config=Configure.Generative.ollama(              # Configure the Ollama generative integration
#     api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
#     model="llama3.2",                                       # The model to use
# )

def create_collection(name: str, vectorizer_config, generative_config):
    return client.collections.create(
        name=name,
        vectorizer_config=vectorizer_config,
        generative_config=generative_config
    )


# products = create_collection("Products", vectorizer_config, generative_config=None)
# articles = create_collection("Articles", vectorizer_config, generative_config=None)
collections = client.collections.list_all(simple=False)

def load_json_data(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)

print("Collection Names: ", list(collections.keys()))
collection = client.collections.get("Products")

def get_object_by_id(collection, id: str):
    object = collection.query.fetch_object_by_id(id)
    if object is None:
        return None
    return object.uuid, object.properties


def delete_object_by_id(collection, id: str):
    try:
        object = get_object_by_id(collection, id)
        collection.data.delete_by_id(id)
        return object
    except Exception as err:
        print("Error deleting object: ", err)
        return None

def add_object_batch(collection, data: list, uuids: list=None):
    try:
        with collection.batch.dynamic() as batch:
            for data_row in data:
                batch.add_object(
                    properties=data_row
                )
                if batch.number_errors > 10:
                    print("Batch import stopped due to excessive errors.")
                    break
        failed_objects = collection.batch.failed_objects
        if failed_objects:
            print(f"Number of failed imports: {len(failed_objects)}")
            print(f"First failed object: {failed_objects[0]}")
        return not failed_objects
    except Exception as err:
        print("Error adding objects: ", err)
        return None

# add_object_batch(collection, load_json_data("data/flipkart_data.json"))

def get_object_count(collection):
    count = 0
    for item in collection.iterator():
        count += 1
    return count

def hybrid_query(collection, query: str, limit: int=3, score: bool=False):
    response = collection.query.hybrid(
        query=query,
        limit=limit,
        return_metadata=MetadataQuery(score=score)
    )
    return response

def semantic_query(collection, query: str, limit: int=3, score: bool=False):
    response = collection.query.near_text(
        query=query,
        limit=limit,
        return_metadata=MetadataQuery(score=score),
        return_properties=["product_name", "description"]
    )
    return response

# # Example of a hybrid/sematic query
query = "256GB phone"
response = hybrid_query(collection, query, limit=3)
response = semantic_query(collection, query, limit=3)
for o in response.objects:
    print(o.uuid, o.properties)

print("Count: ", get_object_count(collection))

client.close()
#################### DUMP ####################

# print(get_object_by_id(collection, "2f5a48f2-704f-4f77-828a-79c6949cd8ff"))
# print(delete_object_by_id(collection, "2f5a48f2-704f-4f77-828a-79c6949cd8ff"))
# print(get_object_by_id(collection, "2f5a48f2-704f-4f77-828a-79c6949cd8ff"))
# if "Products" in collections.keys():
#     data = load_json_data("data/flipkart_data.json")
#     products = client.collections.get("Products")
#     for product in data:
#         products.data.insert(
#             properties=product
#         )
#         break
