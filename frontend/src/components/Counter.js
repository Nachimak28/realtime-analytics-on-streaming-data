import React, { useEffect, useState } from "react";
import "./Counter.css";

const Counter = (props) => {
  const [mean, setMean] = useState(0);
  const [std_dev, setStdDev] = useState(0);
  const [animationData, setAnimationData] = useState("initial");
  const [numberColor, setNumberColor] = useState("green");

  useEffect(() => {
    // 1. Old number goes up
    setTimeout(() => setAnimationData("goUp"), 0);
    // 2. Incrementing the counter
    setTimeout(() => setMean(props.data.mean || 0), 100);
    setTimeout(() => setStdDev(props.data.std_dev || 0), 100);
    // 3. New number waits down
    setTimeout(() => setAnimationData("waitDown"), 100);
    // 4. New number stays in the middle
    setTimeout(() => setAnimationData("initial"), 200);

    if (props.data.mean < 0.5) {
      setNumberColor("red");
    } else {
      setNumberColor("green");
    }
  }, [props]);

  return (
    <div className="Grid">
      <div className="Data">
        <span style={{ fontSize: "35px" }}>Nitrogen</span>
        <br />
        <br />
        <span
          className={animationData}
          style={{ color: numberColor, fontSize: "45px", fontWeight: "bold" }}
        >
          {Number.parseFloat(mean).toFixed(3)} &#177;{" "}
          {Number.parseFloat(std_dev).toFixed(3)}
        </span>
        &nbsp; mg-N/kg
        <br />
        <span style={{ fontSize: "15px", fontWeight: "bold" }}>
          Mean &#177; SD
        </span>
      </div>
    </div>
  );
};

export default Counter;
