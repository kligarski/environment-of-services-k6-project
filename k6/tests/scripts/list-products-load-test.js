import mcp from "k6/x/mcp";
import { check, sleep, group } from "k6";
import { responseText, getRandomQuery } from "./helpers.js";

export const options = {
  vus: 10,
  duration: "1m",
  tags: {
    test_name: "list-products-load-test",
  },
  thresholds: {
    checks: ["rate>0.95"],
    iteration_duration: ["p(95)<3000"],
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: "http://mcp-service:8080/mcp",
  });

  const query = getRandomQuery();

  group("list_products", () => {
    const result = client.callTool({
      name: "list_products",
      arguments: query ? { query } : {},
    });

    check(result, {
      "list_products returns valid response": (r) =>
        responseText(r).includes("Catalog Products:") ||
        responseText(r).includes("No products found matching the criteria."),
    });
  });

  sleep(Math.random() * 1 + 0.2);
}
