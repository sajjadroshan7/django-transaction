import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const UserProfile = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getUserProfile();
  }, []);

  const getUserProfile = () => {
    api
      .get("/api/profile/")
      .then((res) => res.data)
      .then((data) => {
        setUser(data);
        console.log(data);
      })
      .catch((err) => {
        console.error(err);
        alert("Failed to fetch user profile");
        navigate("/login");
      });
  };

  const copySecret = () => {
    if (user?.google_auth_secret) {
      navigator.clipboard.writeText(user.google_auth_secret)
        .then(() => alert("Secret copied to clipboard!"))
        .catch(() => alert("Failed to copy secret."));
    }
  };

  if (!user) {
    return <div style={styles.loading}>Loading...</div>;
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>User Dashboard</h1>
      <div style={styles.card}>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p>
          <strong>Google Auth Secret:</strong> {user.google_auth_secret}{" "}
          <button onClick={copySecret} style={styles.copyButton}>Copy</button>
        </p>
        {user.google_auth_qr && (
          <div style={styles.qrContainer}>
            <p>Google Authenticator QR Code:</p>
            <img
              src={user.google_auth_qr ? `http://localhost:8000${user.google_auth_qr}` : ""}
              alt="Google Authenticator QR"
              style={styles.qrImage}
            />
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "500px",
    margin: "50px auto",
    padding: "20px",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#e0f7fa",
    borderRadius: "15px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
  },
  heading: {
    textAlign: "center",
    marginBottom: "30px",
    color: "#004d40",
    fontSize: "2rem",
    fontWeight: "bold",
  },
  card: {
    border: "1px solid #004d40",
    borderRadius: "12px",
    padding: "20px",
    backgroundColor: "#ffffff",
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
  },
  qrContainer: {
    marginTop: "20px",
    textAlign: "center",
  },
  qrImage: {
    width: "220px",
    height: "220px",
    borderRadius: "10px",
    border: "2px solid #004d40",
    boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
  },
  loading: {
    textAlign: "center",
    marginTop: "50px",
    fontSize: "18px",
    color: "#004d40",
  },
  copyButton: {
    marginLeft: "10px",
    padding: "4px 8px",
    fontSize: "0.9rem",
    cursor: "pointer",
    borderRadius: "4px",
    border: "1px solid #004d40",
    backgroundColor: "#b2dfdb",
  },
};

export default UserProfile;
