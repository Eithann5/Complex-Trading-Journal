export type AlertFeedItem = {
  trigger_id: string;
  alert_id: string | null;
  symbol: string;
  alert_type: string;
  triggered_at_utc: string;
  price: number | null;
  message: string | null;
  condition: Record<string, unknown>;
  snapshot: Record<string, unknown>;
  chart_url: string | null;
};

export type LinkedTriggerItem = {
  trigger_id: string;
  link_type: "trigger" | "context" | "post_entry";
  linked_at_utc: string;
};

export type PositionTagItem = {
  id: string;
  tag: string;
  source: "manual" | "auto";
  created_at_utc: string;
};

export type OpenPositionItem = {
  id: string;
  ticker: string;
  status: "open" | "closed";
  origin: "manual" | "alert_based";
  notes: string | null;
  open_time_utc: string | null;
  close_time_utc: string | null;
  created_at_utc: string;
  tags: PositionTagItem[];
  linked_triggers: LinkedTriggerItem[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function makeUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export async function getAlertsFeed(params?: {
  limit?: number;
  q?: string;
  symbol?: string;
  alert_type?: string;
}): Promise<AlertFeedItem[]> {
  const query = new URLSearchParams();
  if (params?.limit !== undefined) {
    query.set("limit", String(params.limit));
  }
  if (params?.q) {
    query.set("q", params.q);
  }
  if (params?.symbol) {
    query.set("symbol", params.symbol);
  }
  if (params?.alert_type) {
    query.set("alert_type", params.alert_type);
  }
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const res = await fetch(makeUrl(`/api/alerts/feed${suffix}`));
  if (!res.ok) {
    throw new Error(`Failed to fetch alerts feed (${res.status})`);
  }
  return (await res.json()) as AlertFeedItem[];
}

export async function getOpenPositions(): Promise<OpenPositionItem[]> {
  const res = await fetch(makeUrl("/api/positions/open"));
  if (!res.ok) {
    throw new Error(`Failed to fetch open positions (${res.status})`);
  }
  return (await res.json()) as OpenPositionItem[];
}

export async function linkTriggerToPosition(payload: {
  triggerId: string;
  positionId: string;
  linkType: "trigger" | "context" | "post_entry";
}): Promise<void> {
  const res = await fetch(makeUrl(`/api/triggers/${payload.triggerId}/link`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      position_id: payload.positionId,
      link_type: payload.linkType
    })
  });
  if (!res.ok) {
    throw new Error(`Failed to link trigger (${res.status})`);
  }
}

export function resolveStaticUrl(pathOrUrl: string | null): string | null {
  if (!pathOrUrl) {
    return null;
  }
  if (pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")) {
    return pathOrUrl;
  }
  return `${API_BASE_URL}${pathOrUrl}`;
}
