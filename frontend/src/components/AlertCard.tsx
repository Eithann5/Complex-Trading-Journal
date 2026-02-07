import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";

import type { AlertFeedItem } from "../lib/api";
import { resolveStaticUrl } from "../lib/api";

type AlertCardProps = {
  alert: AlertFeedItem;
  onLink: (alert: AlertFeedItem) => void;
};

function formatUtc(value: string): string {
  const date = new Date(value);
  return date.toLocaleString();
}

export default function AlertCard({ alert, onLink }: AlertCardProps) {
  const chartSrc = resolveStaticUrl(alert.chart_url);
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Stack spacing={0.5}>
              <Typography variant="h6">{alert.symbol}</Typography>
              <Typography variant="body2" color="text.secondary">
                Triggered: {formatUtc(alert.triggered_at_utc)}
              </Typography>
            </Stack>
            <Chip label={alert.alert_type} color="primary" variant="outlined" />
          </Stack>

          <Stack direction="row" spacing={2}>
            <Typography variant="body2">
              <strong>Price:</strong>{" "}
              {alert.price !== null ? alert.price.toFixed(2) : "n/a"}
            </Typography>
          </Stack>

          {alert.message ? (
            <Typography variant="body2" color="text.secondary">
              {alert.message}
            </Typography>
          ) : null}

          {chartSrc ? (
            <Box
              component="img"
              src={chartSrc}
              alt={`${alert.symbol} chart`}
              sx={{
                width: "100%",
                borderRadius: 1,
                border: "1px solid",
                borderColor: "divider",
                bgcolor: "background.paper"
              }}
            />
          ) : (
            <Box
              sx={{
                width: "100%",
                py: 4,
                textAlign: "center",
                borderRadius: 1,
                border: "1px dashed",
                borderColor: "divider"
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Chart not available yet.
              </Typography>
            </Box>
          )}

          <Stack direction="row" justifyContent="flex-end">
            <Button variant="contained" onClick={() => onLink(alert)}>
              Link
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
