export function responseText(response) {
  if (response === null || response === undefined) {
    return '';
  }

  if (typeof response === 'string') {
    return response;
  }

  if (response.content && Array.isArray(response.content)) {
    return response.content.map((item) => item.text || '').join('\n');
  }

  if (response.result && response.result.content && Array.isArray(response.result.content)) {
    return response.result.content.map((item) => item.text || '').join('\n');
  }

  return JSON.stringify(response);
}

