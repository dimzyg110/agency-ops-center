const DEFAULT_TIMEOUT_MS = 5000;

function getBaseUrl() {
  return process.env.GLASS_API_URL?.replace(/\/$/, '') || '';
}

function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (process.env.GLASS_API_KEY) {
    headers.Authorization = `Bearer ${process.env.GLASS_API_KEY}`;
    headers['x-api-key'] = process.env.GLASS_API_KEY;
  }

  return headers;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...getHeaders(),
        ...(options.headers || {}),
      },
      signal: controller.signal,
    });

    return response;
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchProducts(operatorId, category) {
  const baseUrl = getBaseUrl();
  if (!baseUrl || !operatorId) {
    console.warn('[glassClient] Missing GLASS_API_URL or operatorId');
    return [];
  }

  try {
    const response = await fetchWithTimeout(`${baseUrl}/api/v1/catalog/${operatorId}/products`);
    if (!response.ok) {
      console.warn(`[glassClient] fetchProducts failed: HTTP ${response.status}`);
      return [];
    }

    const data = await response.json();
    const items = Array.isArray(data?.items) ? data.items : [];

    if (!category || category === 'any') {
      return items;
    }

    const needle = String(category).toLowerCase();
    return items.filter((item) => String(item?.category || '').toLowerCase() === needle);
  } catch (error) {
    console.warn('[glassClient] fetchProducts error:', error?.message || error);
    return [];
  }
}

function postFireAndForget(path, payload) {
  const baseUrl = getBaseUrl();
  if (!baseUrl) {
    return;
  }

  fetchWithTimeout(`${baseUrl}${path}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }).catch((error) => {
    console.warn(`[glassClient] ${path} error:`, error?.message || error);
  });
}

export function logSession(tenantId, operatorId, sessionToken, deviceType, referrer) {
  postFireAndForget('/api/v1/budtender/sessions', {
    tenant_id: tenantId,
    operator_id: operatorId,
    session_token: sessionToken,
    device_type: deviceType,
    referrer,
  });
}

export function logQuery(sessionId, tenantId, queryText, parsedIntent, recommendedProductIds, responseTimeMs) {
  postFireAndForget('/api/v1/budtender/queries', {
    session_id: sessionId,
    tenant_id: tenantId,
    query_text: queryText,
    parsed_intent: parsedIntent,
    recommended_product_ids: recommendedProductIds,
    response_time_ms: responseTimeMs,
  });
}

export default {
  fetchProducts,
  logSession,
  logQuery,
};
