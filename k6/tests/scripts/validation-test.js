import mcp from "k6/x/mcp";
import { check, sleep, group } from "k6";
import { responseText } from "./helpers.js";

export const options = {
  vus: 1,
  iterations: 1,
  tags: {
    test_name: "validation-test",
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: "http://mcp-service:8080/mcp",
  });

  group("list_products_invalid", () => {
    const notFoundName = client.callTool({
      name: "list_products",
      arguments: {
        query: "asdsaddasdasd",
      },
    });

    check(notFoundName, {
      "no products found returned": (r) =>
        responseText(r).includes("No products found matching the criteria."),
    });
  });

  group("get_shipping_quote_invalid", () => {
    const invalidIDQuote = client.callTool({
      name: "get_shipping_quote",
      arguments: {
        items: [{ id: 999999, count: 1 }],
      },
    });

    check(invalidIDQuote, {
      "quote error returned": (r) =>
        responseText(r).includes(
          "Error: One or more Product IDs were not found in the catalog.",
        ),
    });
  });

  group("optimize_packaging_invalid", () => {
    const invalidIDPacking = client.callTool({
      name: "optimize_packaging",
      arguments: {
        items: [{ id: 999999, count: 1 }],
      },
    });

    check(invalidIDPacking, {
      "packing error returned": (r) =>
        responseText(r).includes("Error: Product IDs not found."),
    });
  });
}
