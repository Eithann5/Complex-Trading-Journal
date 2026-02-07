import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Link from "next/link";

export default function HomePage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h4" component="h1">
        Complex Trading Journal
      </Typography>
      <Typography color="text.secondary">
        Use the navigation above or jump directly:
      </Typography>
      <Stack direction="row" spacing={2}>
        <Button component={Link} href="/alerts" variant="contained">
          Go to Alerts
        </Button>
        <Button component={Link} href="/positions" variant="outlined">
          Go to Positions
        </Button>
      </Stack>
    </Stack>
  );
}
