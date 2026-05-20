import mcp from 'k6/x/mcp';
import { check, sleep } from 'k6';
import { responseText } from './helpers.js'

const productIds = [1, 2, 3, 4, 5];

function randomItem() {
    return {
    id: productIds[Math.floor(Math.random() * productIds.length)],
    count: Math.floor(Math.random() * 5) + 1,
    };
}

export const options = {
    vus: 10,
    duration: '1m',
    tags: {
        test_name: 'shipping-quote-load-test',
    },
    thresholds: {
        checks: ['rate>0.95'],
        iteration_duration: ['p(95)<8000'],
    },
};

export default function () {
    const client = new mcp.StreamableHTTPClient({
        base_url: 'http://mcp-service:8080/mcp',
    });

    const result = client.callTool({
        name: 'get_shipping_quote',
        arguments: {items: [randomItem(), randomItem()],},
    });

    check(result, {
    'shipping quote returns valid response': (r) =>
        responseText(r).includes('Available Shipping Quotes'),
    });

    sleep(Math.random() * 1 + 0.5);
}