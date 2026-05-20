import mcp from "k6/x/mcp";
import { check, sleep, group } from "k6";
import { responseText, getRandomItems } from "./helpers.js";

export const options = {
  vus: 10,
  duration: "1m",
  tags: {
    test_name: "shipping-quote-load-test",
  },
  thresholds: {
    checks: ["rate>0.95"],
    iteration_duration: ["p(95)<8000"],
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: "http://mcp-service:8080/mcp",
  });

  group("get_shipping_quote", () => {
    const result = client.callTool({
      name: "get_shipping_quote",
      arguments: { items: getRandomItems(1, 2, 1, 5) },
    });

    check(result, {
      "shipping quote returns valid response": (r) =>
        responseText(r).includes("Available Shipping Quotes"),
    });
  });

  sleep(Math.random() * 1 + 0.5);
}
