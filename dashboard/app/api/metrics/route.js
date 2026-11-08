import { CosmosClient } from "@azure/cosmos";

// This route runs on the SERVER (never in the browser), so the Cosmos key is
// safe here. The browser calls /api/metrics and gets back only the Gold data.
export const dynamic = "force-dynamic"; // always read fresh

export async function GET() {
  const endpoint = process.env.COSMOS_ENDPOINT;
  const key = process.env.COSMOS_KEY;
  const dbName = process.env.COSMOS_DATABASE || "analytics";
  const containerName = process.env.COSMOS_CONTAINER || "metrics";

  if (!endpoint || !key) {
    return Response.json(
      { error: "Cosmos credentials not configured on the server." },
      { status: 500 }
    );
  }

  try {
    const client = new CosmosClient({ endpoint, key });
    const container = client.database(dbName).container(containerName);
    const { resources } = await container.items.readAll().fetchAll();

    // Reshape the 7 metric documents into one keyed object for the UI.
    const out = {};
    for (const doc of resources) {
      out[doc.metric_type] = doc.data;
      if (doc.published_at) out._published_at = doc.published_at;
    }
    return Response.json(out);
  } catch (err) {
    return Response.json({ error: String(err?.message || err) }, { status: 500 });
  }
}
