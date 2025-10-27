import React, { useEffect, useMemo, useState } from 'react';
import { BASE, getAccess, logout } from '../../api/auth';
import './Profile.css';
import { useUser } from '../../context/UserContext';

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
 
  const { user: ctxUser, refreshUser, booting } = useUser();

  const [user, setLocalUser] = useState({
    firstName: '',
    lastName: '',
    email: '',
    role: { id: null, name: '' },
    team: { id: null, name: '' },
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

  useEffect(() => {
    if (booting) { setLoading(true); return; }

    if (!ctxUser) {
      setLoading(false);
      return;
    }

    const newUser = {
      firstName: ctxUser.first_name ?? '',
      lastName : ctxUser.last_name  ?? '',
      email    : ctxUser.email      ?? '',
      role     : { id: ctxUser.role?.id ?? null, name: ctxUser.role?.name ?? '' },
      team     : { id: ctxUser.team?.id ?? null, name: ctxUser.team?.name ?? '' },
      phone    : ctxUser.phone_number ?? '' 
    };

    setLocalUser(newUser);
    setLoading(false);
  }, [ctxUser, booting]);


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setLocalUser(prev => {
      if (name === 'roleName') {
        return { ...prev, role: { ...prev.role, name: value } };
      }
      if (name === 'teamName') {
        return { ...prev, team: { ...prev.team, name: value } };
      }
      return { ...prev, [name]: value };
    });
  };

  const handleSave = async () => {
    try {
      setError(null);
      setIsEditing(false);

      const token = getAccess();
      if (!token) { logout(); return; }

      const payload = {
        first_name: user.firstName,
        last_name : user.lastName,
        email     : user.email,
        phone_number: user.phone,
        role: user.role?.id ? { id: user.role.id } : undefined, 
        team: user.team?.id ? { id: user.team.id } : undefined,
      };

      await fetch(`${BASE}/users/me/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      await refreshUser();
    } catch (e) {
      setError(e.message || 'Erreur de sauvegarde');
    }
  };

  if (booting || loading) {
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
                    name="roleName"
                    value={user.role?.name || ''}
                    onChange={handleInputChange}
                  >
                    <option value="">—</option>
                    <option value="Developer">Developer</option>
                    <option value="Manager">Manager</option>
                    <option value="Designer">Designer</option>
                    <option value="Admin">Admin</option>
                  </select>
                ) : (
                  <span>{displayValue(user.role?.name, 'Rôle')}</span>
                )}
              </div>

              <div className="info-group">
                <label>Équipe</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="teamName"
                    value={user.team?.name || ''}
                    onChange={handleInputChange}
                  />
                ) : (
                  <span>{displayValue(user.team?.name, 'Équipe')}</span>
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
