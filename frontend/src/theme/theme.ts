import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#124e66"
    },
    background: {
      default: "#f4f8fb",
      paper: "#ffffff"
    }
  },
  shape: {
    borderRadius: 10
  }
});
