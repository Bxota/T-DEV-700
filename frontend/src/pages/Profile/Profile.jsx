// src/Profile.jsx
import React, { useEffect, useState } from 'react';
import { BASE, getAccess, logout } from '../../api/auth';
import './Profile.css';

const Profile = () => {
  const [user, setUser] = useState({
    firstName: '',
    lastName: '',
    email: '',
    role: '',
    department: '',
    phone: ''
  });

  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  // Affiche une valeur ou le nom du label si vide/null
  const displayValue = (value, fallbackLabel) =>
    (value === null || value === undefined || value === '') ? fallbackLabel : value;

  // ⬇️ Charger les infos utilisateur via /whoami
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const token = getAccess();
        if (!token) { logout(); return; } // pas de token -> déconnexion

        const res = await fetch(`${BASE}/token/whoami/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });

        if (res.status === 401) { logout(); return; } // token expiré -> déconnexion
        if (!res.ok) throw new Error(`Erreur API: ${res.status}`);

        const data = await res.json();
        const u = data?.user ?? {};

        if (!cancelled) {
          setUser({
            firstName: u.first_name || '',
            lastName:  u.last_name  || '',
            email:     u.email       || '',
            role:      u.role        || '',
            department:u.team        || '',
            phone:     u.phone_number|| ''
          });
        }
      } catch (e) {
        if (!cancelled) setError(e.message || 'Erreur de chargement');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUser(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    setIsEditing(false);
    console.log('Profil sauvegardé:', user);
    // TODO: PUT vers ton endpoint d’update si besoin
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">Mon Profil</h1>
          <p className="page-description">Chargement…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Mon Profil</h1>
        <p className="page-description">Gérez vos informations personnelles et préférences</p>
        {error && <p className="error-banner">⚠️ {error}</p>}
      </div>

      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {displayValue(user.firstName?.[0], 'U')}
              {displayValue(user.lastName?.[0], 'N')}
            </div>
            <button className="change-avatar-btn" disabled={!isEditing}>Changer la photo</button>

            {/* Bouton de déconnexion direct */}
            <button className="cancel-btn" style={{ marginTop: 12 }} onClick={() => logout()}>
              Se déconnecter
            </button>
          </div>

          <div className="profile-info">
            <div className="profile-actions">
              {!isEditing ? (
                <button 
                  className="edit-btn"
                  onClick={() => setIsEditing(true)}
                >
                  ✏️ Modifier
                </button>
              ) : (
                <div className="edit-actions">
                  <button 
                    className="save-btn"
                    onClick={handleSave}
                  >
                    ✅ Sauvegarder
                  </button>
                  <button 
                    className="cancel-btn"
                    onClick={() => setIsEditing(false)}
                  >
                    ❌ Annuler
                  </button>
                </div>
              )}
            </div>

            <div className="info-grid">
              <div className="info-group">
                <label>Prénom</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="firstName"
                    value={user.firstName}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.firstName, 'Prénom')}</span>
                )}
              </div>

              <div className="info-group">
                <label>Nom</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="lastName"
                    value={user.lastName}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.lastName, 'Nom')}</span>
                )}
              </div>

              <div className="info-group">
                <label>Email</label>
                {isEditing ? (
                  <input
                    type="email"
                    name="email"
                    value={user.email}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.email, 'Email')}</span>
                )}
              </div>

              <div className="info-group">
                <label>Téléphone</label>
                {isEditing ? (
                  <input
                    type="tel"
                    name="phone"
                    value={user.phone}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.phone, 'Téléphone')}</span>
                )}
              </div>

              <div className="info-group">
                <label>Rôle</label>
                {isEditing ? (
                  <select
                    name="role"
                    value={user.role}
                    onChange={handleInputChange}
                  >
                    <option value="Developer">Developer</option>
                    <option value="Manager">Manager</option>
                    <option value="Designer">Designer</option>
                    <option value="Admin">Admin</option>
                  </select>
                ) : (
                  <span>{displayValue(user.role, 'Rôle')}</span>
                )}
              </div>

              <div className="info-group">
                <label>Département</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="department"
                    value={user.department}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.department, 'Département')}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
