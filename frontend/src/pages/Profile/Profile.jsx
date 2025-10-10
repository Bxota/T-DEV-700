// src/Profile.jsx
import React, { useEffect, useMemo, useState } from 'react';
import { BASE, getAccess, logout } from '../../api/auth';
import './Profile.css';
import { useUser } from '../../context/UserContext';

// 1) Prénom+Nom -> 2 lettres
// 2) Sinon email (avant @) -> 2 lettres
// 3) Sinon "??"
const computeInitials = ({ firstName, lastName, email }) => {
  const a = (firstName || '').trim();
  const b = (lastName  || '').trim();

  if (a || b) {
    const two = ((a[0] || '') + (b[0] || '')).toUpperCase();
    if (two) return two;
  }
  if (email) {
    const local = (email.split('@')[0] || '').replace(/[^a-z0-9]/gi, '');
    const two = (local.slice(0, 2) || '').toUpperCase();
    if (two) return two;
  }
  return '??';
};

const Profile = () => {
  const { setUser: setCtxUser } = useUser(); // ← pour synchroniser le menu/avatar
  const [user, setLocalUser] = useState({
    firstName: '',
    lastName: '',
    email: '',
    role: '',
    team: '',
    phone: ''
  });

  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const displayValue = (value, fallbackLabel) =>
    (value === null || value === undefined || value === '') ? fallbackLabel : value;

  const initials = useMemo(
    () => computeInitials({
      firstName: user.firstName,
      lastName : user.lastName,
      email    : user.email
    }),
    [user.firstName, user.lastName, user.email]
  );

  // Charger les infos utilisateur via /whoami + MAJ du UserContext pour le menu
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const token = getAccess();
        if (!token) { logout(); return; }

        const res = await fetch(`${BASE}/token/whoami/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });

        if (res.status === 401) { logout(); return; }
        if (!res.ok) throw new Error(`Erreur API: ${res.status}`);

        const data = await res.json();
        const u = data?.user ?? {};

        const newUser = {
          firstName: u.first_name || '',
          lastName:  u.last_name  || '',
          email:     u.email       || '',
          role:      u.role        || '',
          team:      u.team        || '',
          phone:     u.phone_number|| ''
        };

        if (!cancelled) {
          // État local (page profil)
          setLocalUser(newUser);
          // Contexte global (menu/avatar connecté)
          setCtxUser(prev => ({
            ...prev,
            id: u.id ?? prev?.id ?? null,
            email: newUser.email,
            username: prev?.username ?? null,
            first_name: newUser.firstName,
            last_name : newUser.lastName,
            role: newUser.role ?? prev?.role ?? null,
            team: newUser.team ?? prev?.team ?? null,
            avatarUrl: prev?.avatarUrl ?? '' // au cas où tu ajoutes plus tard
          }));
        }
      } catch (e) {
        if (!cancelled) setError(e.message || 'Erreur de chargement');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [setCtxUser]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setLocalUser(prev => ({ ...prev, [name]: value }));
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
            <div className="avatar-circle">{initials}</div>

            <button className="change-avatar-btn" disabled={!isEditing}>
              Changer la photo
            </button>

            <button className="cancel-btn" style={{ marginTop: 12 }} onClick={() => logout()}>
              Se déconnecter
            </button>
          </div>

          <div className="profile-info">
            <div className="profile-actions">
              {!isEditing ? (
                <button className="edit-btn" onClick={() => setIsEditing(true)}>
                  ✏️ Modifier
                </button>
              ) : (
                <div className="edit-actions">
                  <button className="save-btn" onClick={handleSave}>
                    ✅ Sauvegarder
                  </button>
                  <button className="cancel-btn" onClick={() => setIsEditing(false)}>
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
                <label>Équipe</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="team"
                    value={user.team}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.team, 'Équipe')}</span>
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
