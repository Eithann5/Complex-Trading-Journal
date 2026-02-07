import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Link from "next/link";

export default function NavBar() {
  return (
    <AppBar position="static" color="inherit" elevation={1}>
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ gap: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Trading Journal
          </Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button component={Link} href="/alerts" color="primary">
              Alerts
            </Button>
            <Button component={Link} href="/positions" color="primary">
              Positions
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
