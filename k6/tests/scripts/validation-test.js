import mcp from 'k6/x/mcp';
import { check } from 'k6';
import { responseText } from './helpers.js';

export const options = {
  vus: 1,
  iterations: 1,
  tags: {
    test_name: 'validation-test-debug',
  },
};

export default function () {
  const client = new mcp.StreamableHTTPClient({
    base_url: 'http://mcp-service:8080/mcp',
  });

  const notFoundName = client.callTool({
    name: 'list_products',
    arguments: {
      query: 'asdsaddasdasd',
    },
  });

  console.log('NOT_FOUND RAW:', JSON.stringify(notFoundName));
  console.log('NOT_FOUND TEXT:', responseText(notFoundName));

  check(notFoundName, {
    'unknown product returns no products message': (r) =>
      responseText(r).includes('No products found matching the criteria'),
  });

  const invalidIDQuote = client.callTool({
    name: 'get_shipping_quote',
    arguments: {
      items: [{ id: 999999, count: 1 }],
    },
  });

  console.log('INVALID_QUOTE RAW:', JSON.stringify(invalidIDQuote));
  console.log('INVALID_QUOTE TEXT:', responseText(invalidIDQuote));

  check(invalidIDQuote, {
    'invalid quote product id returns error': (r) =>
      responseText(r).includes('Product IDs were not found') ||
      responseText(r).includes('not found'),
  });

  const invalidIDPacking = client.callTool({
    name: 'optimize_packaging',
    arguments: {
      items: [{ id: 999999, count: 1 }],
    },
  });

  console.log('INVALID_PACKING RAW:', JSON.stringify(invalidIDPacking));
  console.log('INVALID_PACKING TEXT:', responseText(invalidIDPacking));

  check(invalidIDPacking, {
    'invalid packaging product id returns error': (r) =>
      responseText(r).includes('Product IDs not found') ||
      responseText(r).includes('valid IDs') ||
      responseText(r).includes('not found'),
  });
}