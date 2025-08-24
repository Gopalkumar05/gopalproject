
import React, { useContext } from "react";
import { AuthContext } from "../AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  return (
    <nav className="navbar">
      <div className="nav-left">MyApp</div>
      <div className="nav-right">
        {user ? (
          <>
            <span className="username">Hello, {user.name}</span>
            <button className="btn" onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <a href="/login" className="btn-link">Login</a>
            <a href="/signup" className="btn-link">Signup</a>
          </>
        )}
      </div>
    </nav>
  );
}
