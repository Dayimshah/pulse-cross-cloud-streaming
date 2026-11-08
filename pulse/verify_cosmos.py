"""verify_cosmos.py - read back the published Gold metrics from Cosmos to
confirm the serving layer is populated. Run: python -m pulse.verify_cosmos"""
from azure.cosmos import CosmosClient

from pulse import config


def run():
    client = CosmosClient(config.COSMOS_ENDPOINT, credential=config.COSMOS_KEY)
    db = client.get_database_client(config.COSMOS_DATABASE)
    container = db.get_container_client(config.COSMOS_CONTAINER)
    items = list(container.read_all_items())
    print(f"Cosmos documents published: {len(items)}\n")
    for it in items:
        mt = it["metric_type"]
        if mt == "funnel":
            print(f"  funnel: {it['data']}")
        elif mt == "totals":
            print(f"  totals: {it['data']}")
        elif mt == "reconciliation":
            print(f"  reconciliation passed: {it['data']['passed']}")
        elif mt == "top_products":
            top = it["data"][:3]
            print(f"  top_products (3): {top}")
        elif mt == "revenue_over_time":
            print(f"  revenue_over_time: {len(it['data'])} daily points")
        elif mt == "retention":
            print(f"  retention: {len(it['data'])} weekly cohorts")
        elif mt == "categories":
            print(f"  categories: {it['data']}")


if __name__ == "__main__":
    run()
