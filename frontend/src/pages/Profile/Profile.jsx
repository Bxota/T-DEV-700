import React, { useState } from 'react';
import './Profile.css';

const Profile = () => {
  const [user, setUser] = useState({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    role: 'Developer',
    department: 'IT',
    phone: '+33 1 23 45 67 89',
    bio: 'Développeur passionné avec 5 ans d\'expérience en React et Node.js.'
  });

  const [isEditing, setIsEditing] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUser(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = () => {
    setIsEditing(false);
    // Ici vous pourriez envoyer les données à votre API
    console.log('Profil sauvegardé:', user);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Mon Profil</h1>
        <p className="page-description">Gérez vos informations personnelles et préférences</p>
      </div>

      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user.firstName[0]}{user.lastName[0]}
            </div>
            <button className="change-avatar-btn">Changer la photo</button>
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
                  <span>{user.firstName}</span>
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
                  <span>{user.lastName}</span>
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
                  <span>{user.email}</span>
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
                  <span>{user.phone}</span>
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
                  <span>{user.role}</span>
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
                  <span>{user.department}</span>
                )}
              </div>

              <div className="info-group full-width">
                <label>Biographie</label>
                {isEditing ? (
                  <textarea
                    name="bio"
                    value={user.bio}
                    onChange={handleInputChange}
                    rows={4}
                  />
                ) : (
                  <span>{user.bio}</span>
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