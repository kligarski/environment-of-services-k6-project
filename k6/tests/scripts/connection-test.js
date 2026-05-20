import mcp from "k6/x/mcp";
import { sleep, group } from "k6";

export const options = {
  vus: 3,
  duration: "30s",
  tags: {
    test_name: "connection-test",
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: "http://mcp-service:8080/mcp",
  });

  group("ping", () => {
    client.ping();
  });

  group("list_products", () => {
    client.callTool({ name: "list_products", arguments: {} });
  });

  group("get_shipping_quote", () => {
    client.callTool({
      name: "get_shipping_quote",
      arguments: { items: [{ id: 1, count: 2 }] },
    });
  });

  group("optimize_packaging", () => {
    client.callTool({
      name: "optimize_packaging",
      arguments: { items: [{ id: 5, count: 10 }] },
    });
  });

  sleep(1);
}
