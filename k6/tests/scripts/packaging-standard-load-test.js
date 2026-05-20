//Made to show that 100% success rate can be achieved for
//packaging, but for lighter options than for list-products and shipping-quote

import mcp from 'k6/x/mcp';
import { check, sleep } from 'k6';
import { responseText } from './helpers.js';

const productIds = [1, 2, 3, 4, 5];

function randomItem() {
    return {
        id: productIds[Math.floor(Math.random() * productIds.length)],
        count: Math.floor(Math.random() * 10) + 1,
    };
}

export const options = {
  vus: 1,
  duration: '30s',
  tags: {
    test_name: 'packaging-standard-load-test',
  },
  thresholds: {
    checks: ['rate>0.80'],
    iteration_duration: ['p(95)<30000'],
  },
};


export default function () {
    const client = new mcp.StreamableHTTPClient({
        base_url: 'http://mcp-service:8080/mcp',
    });

    const result = client.callTool({
        name: 'optimize_packaging',
        arguments: {
            items: [randomItem()],
        },
    });

    check(result, {
        'packaging returns valid response': (r) => {
        const text = responseText(r);
        return (
            text.includes('Packaging Optimization Strategy') ||
            text.includes('Summary') ||
            text.includes('Container')
        );
        },
    });

    sleep(Math.random() * 1 + 0.5);
}
