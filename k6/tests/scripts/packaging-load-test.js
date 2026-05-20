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
    stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
    ],
    tags: {
        test_name: 'packaging-load-test',
    },
    thresholds: {
        checks: ['rate>0.90'],
        iteration_duration: ['p(95)<20000'],
    },
};

export default function () {
    const client = new mcp.StreamableHTTPClient({
        base_url: 'http://mcp-service:8080/mcp',
    });

    const result = client.callTool({
        name: 'optimize_packaging',
        arguments: {
            items: [randomItem(), randomItem(), randomItem()],
        },
    });

    check(result, {
    'packaging returns valid response': (r) =>
        responseText(r).includes('Packaging Optimization Strategy'),
    });

    sleep(Math.random() * 1 + 0.5);
}
