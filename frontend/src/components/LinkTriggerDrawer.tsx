import { useEffect, useMemo, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { AlertFeedItem, OpenPositionItem } from "../lib/api";
import { getOpenPositions, linkTriggerToPosition } from "../lib/api";

type LinkTriggerDrawerProps = {
  open: boolean;
  alert: AlertFeedItem | null;
  onClose: () => void;
  onLinked: (triggerId: string) => void;
};

type LinkType = "trigger" | "context" | "post_entry";

export default function LinkTriggerDrawer({
  open,
  alert,
  onClose,
  onLinked
}: LinkTriggerDrawerProps) {
  const [positions, setPositions] = useState<OpenPositionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [positionId, setPositionId] = useState("");
  const [linkType, setLinkType] = useState<LinkType>("trigger");

  useEffect(() => {
    if (!open) {
      return;
    }
    setError(null);
    setLoading(true);
    void getOpenPositions()
      .then((data) => {
        setPositions(data);
        setPositionId((prev) => (prev ? prev : data[0]?.id ?? ""));
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load positions");
      })
      .finally(() => setLoading(false));
  }, [open]);

  const canSubmit = useMemo(
    () => Boolean(alert && positionId) && !submitting,
    [alert, positionId, submitting]
  );

  async function handleLink(): Promise<void> {
    if (!alert || !positionId) {
      return;
    }
    try {
      setSubmitting(true);
      setError(null);
      await linkTriggerToPosition({
        triggerId: alert.trigger_id,
        positionId,
        linkType
      });
      onLinked(alert.trigger_id);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to link trigger");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 420, p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h6">Link Trigger</Typography>
          <Divider />

          {alert ? (
            <Typography variant="body2" color="text.secondary">
              Trigger: <strong>{alert.symbol}</strong> ({alert.alert_type})
            </Typography>
          ) : null}

          {loading ? (
            <Stack direction="row" spacing={1} alignItems="center">
              <CircularProgress size={18} />
              <Typography variant="body2">Loading open positions...</Typography>
            </Stack>
          ) : (
            <>
              <FormControl fullWidth>
                <InputLabel id="position-id-label">Position</InputLabel>
                <Select
                  labelId="position-id-label"
                  label="Position"
                  value={positionId}
                  onChange={(e) => setPositionId(e.target.value)}
                >
                  {positions.map((position) => (
                    <MenuItem key={position.id} value={position.id}>
                      {position.ticker} | {position.origin} | {position.id.slice(0, 8)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="link-type-label">Link Type</InputLabel>
                <Select
                  labelId="link-type-label"
                  label="Link Type"
                  value={linkType}
                  onChange={(e) => setLinkType(e.target.value as LinkType)}
                >
                  <MenuItem value="trigger">trigger</MenuItem>
                  <MenuItem value="context">context</MenuItem>
                  <MenuItem value="post_entry">post_entry</MenuItem>
                </Select>
              </FormControl>
            </>
          )}

          {error ? <Alert severity="error">{error}</Alert> : null}

          <Stack direction="row" spacing={1} justifyContent="flex-end">
            <Button onClick={onClose} color="inherit">
              Cancel
            </Button>
            <Button
              variant="contained"
              disabled={!canSubmit || loading}
              onClick={() => void handleLink()}
            >
              {submitting ? "Linking..." : "Confirm Link"}
            </Button>
          </Stack>
        </Stack>
      </Box>
    </Drawer>
  );
}
