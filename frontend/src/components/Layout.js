import React from "react";
import Plant from "./Plant";
import Counter from "./Counter";
import { Grid, Paper } from "@mui/material";

export default function Layout(props) {
  return (
    <div>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Grid container direction="column">
            <Grid item xs={6}>
              <div style={{ marginLeft: "15%", height: "25%" }}>
                <Paper elevation={0} style={{ height: "20%" }}>
                  <p style={{ fontSize: "65px", marginBottom: "0" }}>
                    PlantMax
                  </p>
                  <p style={{ fontSize: "20px", margin: "0" }}>
                    Your personal Plant care companion
                  </p>
                </Paper>
              </div>
            </Grid>
            <Grid item xs={6}>
              <Paper
                elevation={0}
                style={{
                  backgroundColor: "#F0F5D1",
                  // textAlign: "center",
                  width: "60%",
                  height: "50%",
                  marginLeft: "15%",
                  marginTop: "5%",
                  padding: "5%",
                  borderRadius: "5%",
                }}
              >
                <Counter data={props.data} />
              </Paper>
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={6}>
          <Plant data={props.data} />
        </Grid>
      </Grid>
    </div>
  );
}
