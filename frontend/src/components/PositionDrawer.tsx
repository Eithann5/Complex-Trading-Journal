import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import FormControl from "@mui/material/FormControl";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import type { OpenPositionItem } from "../lib/api";
import { addPositionTag, deletePositionTag, patchPosition } from "../lib/api";

type PositionDrawerProps = {
  open: boolean;
  position: OpenPositionItem | null;
  onClose: () => void;
  onSaved: (position: OpenPositionItem) => void;
};

export default function PositionDrawer({
  open,
  position,
  onClose,
  onSaved
}: PositionDrawerProps) {
  const [origin, setOrigin] = useState<"manual" | "alert_based">("manual");
  const [notes, setNotes] = useState("");
  const [newTag, setNewTag] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!position) {
      return;
    }
    setOrigin(position.origin);
    setNotes(position.notes ?? "");
    setNewTag("");
    setError(null);
  }, [position]);

  async function handleSave(): Promise<void> {
    if (!position) {
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const updated = await patchPosition(position.id, {
        origin,
        notes: notes.trim() ? notes : null
      });
      onSaved(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save position");
    } finally {
      setSaving(false);
    }
  }

  async function handleAddTag(): Promise<void> {
    if (!position || !newTag.trim()) {
      return;
    }
    try {
      setSaving(true);
      setError(null);
      await addPositionTag({
        positionId: position.id,
        tag: newTag.trim(),
        source: "manual"
      });
      const updated = await patchPosition(position.id, {
        origin,
        notes: notes.trim() ? notes : null
      });
      onSaved(updated);
      setNewTag("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add tag");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteTag(tagId: string): Promise<void> {
    if (!position) {
      return;
    }
    try {
      setSaving(true);
      setError(null);
      await deletePositionTag({ positionId: position.id, tagId });
      const updated = await patchPosition(position.id, {
        origin,
        notes: notes.trim() ? notes : null
      });
      onSaved(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to remove tag");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 440, p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h6">
            {position ? `${position.ticker} Position` : "Position"}
          </Typography>
          <Divider />

          <FormControl fullWidth>
            <InputLabel id="origin-select-label">Origin</InputLabel>
            <Select
              labelId="origin-select-label"
              label="Origin"
              value={origin}
              onChange={(e) => setOrigin(e.target.value as "manual" | "alert_based")}
            >
              <MenuItem value="manual">manual</MenuItem>
              <MenuItem value="alert_based">alert_based</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Notes"
            multiline
            minRows={4}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <Stack spacing={1}>
            <Typography variant="subtitle2">Tags</Typography>
            <Stack direction="row" spacing={1}>
              <TextField
                size="small"
                label="Add tag"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                fullWidth
              />
              <Button variant="outlined" onClick={() => void handleAddTag()} disabled={saving}>
                Add
              </Button>
            </Stack>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {(position?.tags ?? []).map((tag) => (
                <Chip
                  key={tag.id}
                  label={tag.tag}
                  onDelete={() => void handleDeleteTag(tag.id)}
                />
              ))}
            </Stack>
          </Stack>

          <Stack spacing={1}>
            <Typography variant="subtitle2">Linked Triggers</Typography>
            {(position?.linked_triggers ?? []).length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No linked triggers.
              </Typography>
            ) : (
              <Stack spacing={0.5}>
                {position?.linked_triggers.map((item) => (
                  <Typography key={`${item.trigger_id}-${item.linked_at_utc}`} variant="body2">
                    {item.trigger_id} • {item.link_type} •{" "}
                    {new Date(item.linked_at_utc).toLocaleString()}
                  </Typography>
                ))}
              </Stack>
            )}
          </Stack>

          {error ? <Alert severity="error">{error}</Alert> : null}

          <Stack direction="row" spacing={1} justifyContent="flex-end">
            <Button onClick={onClose} color="inherit">
              Close
            </Button>
            <Button variant="contained" onClick={() => void handleSave()} disabled={saving}>
              Save
            </Button>
          </Stack>
        </Stack>
      </Box>
    </Drawer>
  );
}
