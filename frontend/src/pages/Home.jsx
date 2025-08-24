
import React, { useContext } from "react";
import { AuthContext } from "../AuthContext";

export default function Home() {
  const { user } = useContext(AuthContext);
  return (
    <>

    <div className="page">
       
      <h1>Welcome {user ? user.name : "Guest"}</h1>
      {user ? <p>Glad to see you, {user.name}!</p> : <p>Please login or signup to see personalized content.</p>}
    </div>
    </>
  );
}
