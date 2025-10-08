import React, { useState } from 'react';
import './Login.css';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';

const Login = () => {
  const { setUser } = useUser();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState(''); 
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();

    try {
      const nameFromEmail = email.split('@')[0];
      const fakeUser = {
        id: Date.now().toString(),
        email,
        name: nameFromEmail.charAt(0).toUpperCase() + nameFromEmail.slice(1),
      };

      setUser(fakeUser);   
      navigate('/');       
    } catch (err) {
      setError('Une erreur est survenue');
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
              autoComplete="email"
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

          {error && <p style={{ color: 'crimson', marginTop: 8 }}>{error}</p>}

          <button type="submit" className="login-button">Se connecter</button>
        </form>

        <p className="register-text">
          Pas encore de compte ? <a href="/register">Créer un compte</a>
        </p>
      </div>
    </div>
  );
};

export default Login;