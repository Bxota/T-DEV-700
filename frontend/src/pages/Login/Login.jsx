import React, { useState } from "react";
import "./Login.css";
import { useNavigate } from "react-router-dom";
import { useUser } from "../../context/UserContext";
import { login } from "../../api/auth";           // ⬅️ whoami supprimé

export default function Login() {
  const { setUser } = useUser();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");   // string only
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      const { claims } = await login(email.trim(), password);

      // construit un user sans appeler whoami
      const user = {
        id: claims?.user_id ?? claims?.sub ?? null,
        email: claims?.email ?? email.trim(),
        username: claims?.username ?? null,
      };

      setUser(user);
      navigate("/");
    } catch (err) {
      // 🔒 Toujours une string -> évite "Objects are not valid as a React child"
      const msg =
        err?.message ||
        "Impossible de contacter le serveur.";
      setErrorMsg(String(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Connexion</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="Entrez votre email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          <div className="input-group">
            <label>Mot de passe</label>
            <input
              type="password"
              placeholder="Entrez votre mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {errorMsg ? (
            <p style={{ color: "crimson", marginTop: 8 }}>
              {errorMsg}
            </p>
          ) : null}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        <p className="register-text">
          Pas encore de compte ? <a href="/register">Créer un compte</a>
        </p>
      </div>
    </div>
  );
}
