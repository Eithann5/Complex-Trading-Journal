import type { AppProps } from "next/app";
import Container from "@mui/material/Container";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import { ThemeProvider } from "@mui/material/styles";

import NavBar from "../components/NavBar";
import { theme } from "../theme/theme";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <NavBar />
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Component {...pageProps} />
        </Box>
      </Container>
    </ThemeProvider>
  );
}
