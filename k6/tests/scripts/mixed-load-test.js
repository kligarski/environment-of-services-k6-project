import mcp from "k6/x/mcp";
import { check, sleep, group } from "k6";
import { responseText, getRandomQuery, getRandomItems } from "./helpers.js";

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 20 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    checks: ["rate>0.95"],
    iteration_duration: ["p(95)<10000"],
  },
  tags: {
    test_name: "mixed-load-test",
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: "http://mcp-service:8080/mcp",
  });

  group("list_products", () => {
    const query = getRandomQuery();
    const products = client.callTool({
      name: "list_products",
      arguments: query ? { query } : {},
    });

    check(products, {
      "list products returns valid response": (r) =>
        responseText(r).includes("Catalog Products:") ||
        responseText(r).includes("No products found"),
    });
  });

  group("get_shipping_quote", () => {
    const quote = client.callTool({
      name: "get_shipping_quote",
      arguments: {
        items: getRandomItems(1, 2, 1, 5),
      },
    });

    check(quote, {
      "shipping quote returns valid response": (r) =>
        responseText(r).includes("Available Shipping Quotes:"),
    });
  });

  group("optimize_packaging", () => {
    const packaging = client.callTool({
      name: "optimize_packaging",
      arguments: {
        items: getRandomItems(2, 4, 1, 7),
      },
    });

    check(packaging, {
      "optimize packaging returns valid response": (r) =>
        responseText(r).includes("Packaging Optimization Strategy:"),
    });
  });

  sleep(1);
}
