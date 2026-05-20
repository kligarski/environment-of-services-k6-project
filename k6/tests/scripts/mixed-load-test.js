import mcp from 'k6/x/mcp';
import { check, sleep } from 'k6';
import { responseText } from './helpers.js';

export const options = {
    vus: 10,
    duration: '2m',
    thresholds: {
        checks: ['rate>0.95'],
        iteration_duration: ['p(95)<5000']
    },
    tags: {
        test_name: 'mixed-load-test',
    },
};

export default function () {
    const client = new mcp.StreamableHTTPClient({
        base_url: 'http://mcp-service:8080/mcp',
    });


    const products = client.callTool({ 
        name: 'list_products', arguments: {} 
    });

    check(products, {
        'list products returns valid response': (r) => responseText(r).includes(
        'Catalog Products:')
    });


    const quote = client.callTool({
        name: 'get_shipping_quote',
        arguments: {
        items: [{ id: 1, count: 2 }],
        },
    });

    check(quote, {
        'shipping quote returns valid response': (r) => responseText(r).includes(
        'Available Shipping Quotes:')
    });


    const packaging = client.callTool({
        name: 'optimize_packaging',
        arguments: {
        items: [{ id: 5, count: 10 }],
        },
    });

    check(packaging, {
        'optimize packaging returns valid response': (r) => responseText(r).includes(
        'Packaging Optimization Strategy:')
    });

    sleep(1);
}