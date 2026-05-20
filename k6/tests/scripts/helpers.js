export function responseText(response) {
  if (response === null || response === undefined) {
    return "";
  }

  if (typeof response === "string") {
    return response;
  }

  if (response.content && Array.isArray(response.content)) {
    return response.content.map((item) => item.text || "").join("\n");
  }

  if (
    response.result &&
    response.result.content &&
    Array.isArray(response.result.content)
  ) {
    return response.result.content.map((item) => item.text || "").join("\n");
  }

  return JSON.stringify(response);
}

const productIds = [1, 2, 3, 4, 5];

export function getRandomProduct() {
  return productIds[Math.floor(Math.random() * productIds.length)];
}

export function getRandomItems(
  minLines = 1,
  maxLines = 3,
  minCount = 1,
  maxCount = 10,
) {
  const lines =
    Math.floor(Math.random() * (maxLines - minLines + 1)) + minLines;
  const items = [];
  for (let i = 0; i < lines; i++) {
    items.push({
      id: getRandomProduct(),
      count: Math.floor(Math.random() * (maxCount - minCount + 1)) + minCount,
    });
  }
  return items;
}

export const queries = ["", "laptop", "chair", "smartphone", "router"];

export function getRandomQuery() {
  return queries[Math.floor(Math.random() * queries.length)];
}
