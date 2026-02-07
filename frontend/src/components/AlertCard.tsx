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
  const now = new Date();
  const deltaMs = now.getTime() - date.getTime();
  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;

  const isSameDay =
    now.getFullYear() === date.getFullYear() &&
    now.getMonth() === date.getMonth() &&
    now.getDate() === date.getDate();

  if (isSameDay) {
    if (deltaMs < hourMs) {
      const minutes = Math.max(1, Math.floor(deltaMs / minuteMs));
      if (minutes <= 1) {
        return "Just now";
      }
      return `${minutes} minutes ago`;
    }
    const hours = Math.max(1, Math.floor(deltaMs / hourMs));
    return `${hours} hours ago`;
  }

  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  const isYesterday =
    yesterday.getFullYear() === date.getFullYear() &&
    yesterday.getMonth() === date.getMonth() &&
    yesterday.getDate() === date.getDate();
  if (isYesterday) {
    return `Yesterday at ${date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    })}`;
  }

  const datePart = date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
    year: "numeric"
  });
  const timePart = date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  });
  return `${datePart} · ${timePart}`;
}

export default function AlertCard({ alert, onLink }: AlertCardProps) {
  const chartSrc = resolveStaticUrl(alert.chart_url);
  const metaLine =
    `${formatUtc(alert.triggered_at_utc)} • ` +
    `Price ${alert.price !== null ? `$${alert.price.toFixed(2)}` : "$n/a"}`;

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={1.5}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            spacing={1}
          >
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                {alert.symbol}
              </Typography>
              <Chip label={alert.alert_type} color="primary" variant="outlined" />
            </Stack>
            <Button variant="contained" onClick={() => onLink(alert)}>
              Link
            </Button>
          </Stack>

          <Typography variant="body2" color="text.secondary">
            {metaLine}
          </Typography>

          {alert.message ? (
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: 13 }}>
              {alert.message}
            </Typography>
          ) : null}

          {chartSrc ? (
            <Box
              component="img"
              src={chartSrc}
              alt={`${alert.symbol} chart`}
              loading="lazy"
              sx={{
                width: "100%",
                height: "auto",
                display: "block",
                objectFit: "contain",
                imageRendering: "auto",
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
        </Stack>
      </CardContent>
    </Card>
  );
}
