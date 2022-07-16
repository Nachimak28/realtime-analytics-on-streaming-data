import React from "react";
import { useState, useEffect } from "react";
import HealthyPlant from "../assets/illustration_1.png";
import StressedPlant from "../assets/illustration_3.png";

const Plant = (props) => {
  const [plantImg, setPlantImg] = useState(HealthyPlant);

  const style_1 = {
    float: "center",
    marginRight: "10%",
    marginTop: "15%",
    background:
      "radial-gradient(circle, rgba(209,238,219, 1) 0%, rgba(255,255,255,1) 55%)",
  };

  const style_2 = {
    float: "center",
    marginRight: "10%",
    marginTop: "15%",
    background:
      "radial-gradient(circle, rgba(237,89,73,1) 0%, rgba(255,255,255,1) 55%)",
  };

  useEffect(() => {
    if (props.data.mean < 0.5) {
      setPlantImg(StressedPlant);
    } else {
      setPlantImg(HealthyPlant);
    }
  }, [props]);

  return (
    <div style={props.data.mean < 0.5 ? style_2 : style_1}>
      <img src={plantImg} alt="plant" height="500px" width="auto"></img>
    </div>
  );
};

export default Plant;
