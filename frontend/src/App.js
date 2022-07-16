import React, { useState, useEffect } from "react";
import io from "socket.io-client";
import Layout from "./components/Layout";
import './App.css';

const socket = io("http://your_ip_here");

function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [sensorData, setSensorData] = useState({});

  async function fetchLatestDbEntry() {
    const response = await fetch("http://your_ip_here/be/initvalue");
    const data = await response.json();
    setSensorData(data);
  }

  useEffect(() => {
    socket.on("connect", () => {
      setIsConnected(true);
    });

    socket.on("disconnect", () => {
      setIsConnected(false);
    });

    fetchLatestDbEntry();

    socket.on("newMessage", (message) => {
      setSensorData(message);
      return message;
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
    };
  }, []);

  return (
    <div>
      {console.log("Websocket Connected: ", isConnected)}
      {isConnected ? (
        <Layout data={sensorData} />
      ) : (
        <div>Nothing to see here</div>
      )}
    </div>
  );
}

export default App;
