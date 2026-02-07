import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

import PositionDrawer from "../components/PositionDrawer";
import type { OpenPositionItem } from "../lib/api";
import { getOpenPositions } from "../lib/api";

const COLUMNS = [
  "ticker",
  "last",
  "position",
  "mkt value",
  "chg %",
  "P&L",
  "Unrlzd P&L",
  "Unrlzd P&L %"
] as const;

export default function PositionsPage() {
  const [positions, setPositions] = useState<OpenPositionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<OpenPositionItem | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    void loadPositions();
  }, []);

  async function loadPositions(): Promise<void> {
    try {
      setLoading(true);
      const data = await getOpenPositions();
      setPositions(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load positions");
    } finally {
      setLoading(false);
    }
  }

  function openDrawer(position: OpenPositionItem): void {
    setSelectedPosition(position);
    setDrawerOpen(true);
  }

  function closeDrawer(): void {
    setDrawerOpen(false);
  }

  function handlePositionSaved(updated: OpenPositionItem): void {
    setPositions((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    setSelectedPosition(updated);
  }

  return (
    <Stack spacing={3}>
      <Stack spacing={1}>
        <Typography variant="h4" component="h1">
          Positions
        </Typography>
        <Typography color="text.secondary">
          Open positions journal. Click a row to edit origin, tags, and notes.
        </Typography>
      </Stack>

      {loading ? (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={18} />
          <Typography variant="body2">Loading open positions...</Typography>
        </Stack>
      ) : null}

      {error ? <Alert severity="error">{error}</Alert> : null}

      {!loading && !error && positions.length === 0 ? (
        <Box sx={{ py: 4 }}>
          <Typography color="text.secondary">No open positions found.</Typography>
        </Box>
      ) : null}

      {positions.length > 0 ? (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                {COLUMNS.map((column) => (
                  <TableCell key={column} sx={{ fontWeight: 700 }}>
                    {column}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {positions.map((position) => (
                <TableRow
                  key={position.id}
                  hover
                  onClick={() => openDrawer(position)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell>{position.ticker}</TableCell>
                  <TableCell>--</TableCell>
                  <TableCell>--</TableCell>
                  <TableCell>--</TableCell>
                  <TableCell>--</TableCell>
                  <TableCell>--</TableCell>
                  <TableCell>--</TableCell>
                  <TableCell>--</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : null}

      <PositionDrawer
        open={drawerOpen}
        position={selectedPosition}
        onClose={closeDrawer}
        onSaved={handlePositionSaved}
      />
    </Stack>
  );
}
