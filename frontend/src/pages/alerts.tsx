import { useCallback, useEffect, useMemo, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import AlertCard from "../components/AlertCard";
import LinkTriggerDrawer from "../components/LinkTriggerDrawer";
import type { AlertFeedItem } from "../lib/api";
import { getAlertsFeed } from "../lib/api";

const DEFAULT_POLL_MS = 7000;
const POLL_INTERVAL_MS = Number(process.env.NEXT_PUBLIC_ALERTS_POLL_MS ?? DEFAULT_POLL_MS);

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertFeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [selectedAlert, setSelectedAlert] = useState<AlertFeedItem | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const normalizedQuery = useMemo(() => query.trim(), [query]);

  const loadAlerts = useCallback(async () => {
    try {
      const data = await getAlertsFeed({
        limit: 50,
        q: normalizedQuery || undefined
      });
      setAlerts(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load alerts");
    } finally {
      setLoading(false);
    }
  }, [normalizedQuery]);

  useEffect(() => {
    setLoading(true);
    void loadAlerts();
  }, [loadAlerts]);

  useEffect(() => {
    function shouldPoll(): boolean {
      if (typeof document === "undefined") {
        return true;
      }
      return document.visibilityState === "visible";
    }

    const intervalId = window.setInterval(() => {
      if (shouldPoll()) {
        void loadAlerts();
      }
    }, POLL_INTERVAL_MS);

    return () => window.clearInterval(intervalId);
  }, [loadAlerts]);

  function openLinkDrawer(alert: AlertFeedItem): void {
    setSelectedAlert(alert);
    setDrawerOpen(true);
  }

  function closeLinkDrawer(): void {
    setDrawerOpen(false);
  }

  function handleLinked(triggerId: string): void {
    setAlerts((prev) => prev.filter((item) => item.trigger_id !== triggerId));
  }

  return (
    <Stack spacing={3}>
      <Stack spacing={1}>
        <Typography variant="h4" component="h1">
          Alerts
        </Typography>
        <Typography color="text.secondary">
          Unlinked trigger feed with inline charts. Polling every {Math.round(POLL_INTERVAL_MS / 1000)}s.
        </Typography>
      </Stack>

      <TextField
        label="Search symbol or alert type"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g. CVCO or sma_touch"
      />

      {loading ? (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={18} />
          <Typography variant="body2">Loading alerts...</Typography>
        </Stack>
      ) : null}

      {error ? <Alert severity="error">{error}</Alert> : null}

      {!loading && !error && alerts.length === 0 ? (
        <Box sx={{ py: 4 }}>
          <Typography color="text.secondary">No unlinked alerts found.</Typography>
        </Box>
      ) : null}

      <Stack spacing={2}>
        {alerts.map((alert) => (
          <AlertCard key={alert.trigger_id} alert={alert} onLink={openLinkDrawer} />
        ))}
      </Stack>

      <LinkTriggerDrawer
        open={drawerOpen}
        alert={selectedAlert}
        onClose={closeLinkDrawer}
        onLinked={handleLinked}
      />
    </Stack>
  );
}
