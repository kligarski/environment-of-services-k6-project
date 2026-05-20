import mcp from "k6/x/mcp";
import { check, sleep, group } from "k6";
import { responseText, getRandomItems } from "./helpers.js";

export const options = {
  vus: 10,
  duration: "1m",
  tags: {
    test_name: "packaging-load-test",
  },
  thresholds: {
    checks: ["rate>0.90"],
    iteration_duration: ["p(95)<10000"],
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: "http://mcp-service:8080/mcp",
  });

  group("optimize_packaging", () => {
    // Occasionally use more items (up to 25 total) to test performance
    const items = getRandomItems(2, 4, 1, 7);

    const result = client.callTool({
      name: "optimize_packaging",
      arguments: { items: items },
    });

    check(result, {
      "packaging returns valid response": (r) =>
        responseText(r).includes("Packaging Optimization Strategy"),
    });
  });

  sleep(Math.random() * 1 + 0.5);
}
