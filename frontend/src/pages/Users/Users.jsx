import React, { useState, useEffect } from 'react';
import './Users.css';
import { getAuthHeaders } from '../../api/auth';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [roles, setRoles] = useState([]);
  const [viewingUser, setViewingUser] = useState(null);
  const [editingUser, setEditingUser] = useState(null);
  const [deletingUser, setDeletingUser] = useState(null);
  const [addingUser, setAddingUser] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [currentUser, setCurrentUser] = useState(() => {
    const storedUser = localStorage.getItem('user');
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const [newUserData, setNewUserData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    team_id: null,
    role_id: null
  });
  const [errorModal, setErrorModal] = useState({ show: false, message: '', title: '' });

  // Fonction utilitaire pour obtenir le nom du rôle
  const getRoleName = (user) => {
    // Si l'utilisateur a un objet role, utiliser role.name
    if (user.role && user.role.name) {
      return user.role.name;
    }
    // Sinon, chercher dans la liste des rôles avec role_id
    if (user.role_id) {
      const role = roles.find(r => r.id === user.role_id);
      return role ? role.name : 'Non défini';
    }
    return 'Non défini';
  };

  // Récupération des données depuis l'API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Récupération des rôles
        const rolesResponse = await fetch('/api/roles/', {
            headers: getAuthHeaders()   
        });
        if (rolesResponse.ok) {
            const rolesData = await rolesResponse.json();
            console.log('Roles récupérés:', rolesData);
            setRoles(Array.isArray(rolesData) ? rolesData : Array.isArray(rolesData.roles) ? rolesData.roles : []);
        }

        // Récupération des utilisateurs
        const usersResponse = await fetch('/api/users/', {
          headers: getAuthHeaders()
        });
        
        if (!usersResponse.ok) {
          throw new Error(`Erreur users: ${usersResponse.status}`);
        }
        
        const usersData = await usersResponse.json();
        const usersList = Array.isArray(usersData) ? usersData : 
                         Array.isArray(usersData.users) ? usersData.users : [];
        setUsers(usersList);
        console.log('Users récupérés:', usersList);

        // Récupération des équipes
        const teamsResponse = await fetch('/api/teams/', {
          headers: getAuthHeaders()
        });
        
        if (teamsResponse.ok) {
          const teamsData = await teamsResponse.json();
          const teamsList = Array.isArray(teamsData) ? teamsData :
                           Array.isArray(teamsData.teams) ? teamsData.teams : [];
          setTeams(teamsList);
          console.log('Teams récupérées:', teamsList);
        }
        
      } catch (err) {
        console.error('Erreur lors de la récupération des données:', err);
        setError(err.message);
        setUsers([]);
        setTeams([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const openAddUser = () => {
    setAddingUser(true);
    setNewUserData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      team_id: null,
      role_id: null
    });
    setSelectedTeam('');
    setSelectedRole('');
  };

  const closeAddUser = () => {
    setAddingUser(false);
    setNewUserData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      team_id: null,
      role_id: null
    });
    setSelectedTeam('');
    setSelectedRole('');
  };

  // Fonction pour afficher la modal d'erreur
  const showErrorModal = (title, message) => {
    setErrorModal({ show: true, title, message });
  };

  const closeErrorModal = () => {
    setErrorModal({ show: false, message: '', title: '' });
  };

  const handleAddUser = async () => {
    // Validation complète des champs obligatoires
    if (!newUserData.email.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un email');
      return;
    }
    if (!newUserData.password.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un mot de passe');
      return;
    }
    if (!newUserData.first_name.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un prénom');
      return;
    }
    if (!newUserData.last_name.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un nom');
      return;
    }
    if (!selectedRole) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner un rôle');
      return;
    }

    console.log('Création utilisateur - Données saisies:', newUserData, selectedTeam, selectedRole);
    try {
      const payload = {
        ...newUserData,
        team_id: selectedTeam ? parseInt(selectedTeam) : null,
        role_id: selectedRole ? parseInt(selectedRole) : null
      };

      console.log('Création utilisateur - Données envoyées:', payload);
      
      const response = await fetch('/api/users/', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Nouvel utilisateur créé:', responseData);
        
        const newUser = responseData.user || responseData;
        
        // Ajouter l'équipe au nouvel utilisateur si sélectionnée
        if (selectedTeam) {
          const selectedTeamData = teams.find(t => t.id === parseInt(selectedTeam));
          newUser.team = selectedTeamData;
        }
        
        // Ajouter le rôle au nouvel utilisateur
        if (selectedRole) {
          const selectedRoleData = roles.find(r => r.id === parseInt(selectedRole));
          newUser.role = selectedRoleData;
        }
        
        setUsers(prev => [...prev, newUser]);
        closeAddUser();
      } else {
        let errorMessage = 'Erreur lors de la création de l\'utilisateur';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de création', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  const openView = (user) => setViewingUser(user);
  const closeView = () => setViewingUser(null);

  const openEdit = (user) => {
    setEditingUser({ ...user });
    setSelectedTeam(user.team ? user.team.id.toString() : '');
    // Utiliser user.role.id si disponible, sinon user.role_id
    const roleId = user.role ? user.role.id : user.role_id;
    setSelectedRole(roleId ? roleId.toString() : '');
  };
  const closeEdit = () => {
    setEditingUser(null);
    setSelectedTeam('');
    setSelectedRole('');
  };

  const handleSave = async () => {
    // Validation complète des champs obligatoires pour la modification
    if (!editingUser.email.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un email');
      return;
    }
    if (!editingUser.first_name.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un prénom');
      return;
    }
    if (!editingUser.last_name.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un nom');
      return;
    }
    if (!selectedRole) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner un rôle');
      return;
    }

    try {
      const payload = {
        email: editingUser.email,
        first_name: editingUser.first_name,
        last_name: editingUser.last_name,
        team_id: selectedTeam ? parseInt(selectedTeam) : null,
        role_id: selectedRole ? parseInt(selectedRole) : null
      };
      
      console.log('Modification utilisateur - Données envoyées:', payload);
      
      const response = await fetch(`/api/users/${editingUser.id}/`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Réponse de l\'API:', responseData);

        const updatedUser = {
          ...editingUser,
          email: responseData.email || editingUser.email,
          first_name: responseData.first_name || editingUser.first_name,
          last_name: responseData.last_name || editingUser.last_name,
          // Gérer les deux formats possibles du rôle
          role: responseData.role || (selectedRole ? roles.find(r => r.id === parseInt(selectedRole)) : null),
          role_id: responseData.role_id || (selectedRole ? parseInt(selectedRole) : null),
          team: selectedTeam ? teams.find(t => t.id === parseInt(selectedTeam)) : null
        };

        setUsers(prev => prev.map(user => 
          user.id === editingUser.id ? updatedUser : user
        ));

        if (viewingUser?.id === editingUser.id) {
          setViewingUser(updatedUser);
        }

        closeEdit();
      } else {
        let errorMessage = 'Erreur lors de la modification de l\'utilisateur';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de modification', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  const askDelete = (user) => setDeletingUser(user);
  const cancelDelete = () => setDeletingUser(null);
  
  const confirmDelete = async () => {
    try {
      const response = await fetch(`/api/users/${deletingUser.id}/`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        setUsers(prev => prev.filter(u => u.id !== deletingUser.id));
        if (viewingUser?.id === deletingUser.id) setViewingUser(null);
        if (editingUser?.id === deletingUser.id) setEditingUser(null);
        setDeletingUser(null);
      } else {
        let errorMessage = 'Erreur lors de la suppression de l\'utilisateur';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        
        setDeletingUser(null);
        showErrorModal('Erreur de suppression', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      setDeletingUser(null);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };



  // Pour accéder à l'ID :
  // currentUser?.id

  // Pour accéder à l'email :
  // currentUser?.email

  // etc...

  if (loading) {
    return (
      <div className="users-page-container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <p>Chargement des utilisateurs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="users-page-container">
        <div style={{ textAlign: 'center', padding: '50px', color: 'red' }}>
          <p>Erreur: {error}</p>
          <button onClick={() => window.location.reload()}>
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="users-page-container">
      <div className="users-page-header">
        <h1 className="users-page-title">Utilisateurs</h1>
        <p className="users-page-description">Gestion des utilisateurs de l'entreprise</p>
        <button className="users-add-button" onClick={openAddUser}>
          + Ajouter un utilisateur
        </button>
      </div>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>Nom</th>
              <th>Email</th>
              <th>Rôle</th>
              <th>Équipe</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} onClick={() => openView(user)} style={{ cursor: 'pointer' }}>
                <td>
                  {user.first_name && user.last_name ? 
                    `${user.first_name} ${user.last_name}` : 
                    user.username || 'Nom non défini'
                  }
                </td>
                <td>{user.email || 'Email non défini'}</td>
                <td>{getRoleName(user)}</td>
                <td>{user.team ? user.team.name : 'Aucune équipe'}</td>
                <td className="users-actions-cell" onClick={(e) => e.stopPropagation()}>
                  <button className="users-btn users-btn-edit" onClick={() => openEdit(user)}>
                    Modifier
                  </button>
                  {currentUser?.id !== user.id && (
                    <button className="users-btn users-btn-delete" onClick={() => askDelete(user)}>
                      Supprimer
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {users.length === 0 && !loading && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                  {error ? 'Erreur lors du chargement des utilisateurs' : 'Aucun utilisateur enregistré'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal pour ajouter un utilisateur */}
      {addingUser && (
        <div className="users-modal-overlay" onClick={closeAddUser}>
          <div className="users-modal users-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="users-modal-header">
              <h2>Ajouter un utilisateur</h2>
              <button className="users-modal-close" onClick={closeAddUser}>
                ×
              </button>
            </div>

            <label>Email *</label>
            <input
              type="email"
              value={newUserData.email}
              onChange={(e) => setNewUserData({...newUserData, email: e.target.value})}
              placeholder="Saisir l'email"
              autoFocus
            />

            <label>Mot de passe *</label>
            <input
              type="password"
              value={newUserData.password}
              onChange={(e) => setNewUserData({...newUserData, password: e.target.value})}
              placeholder="Saisir le mot de passe"
            />

            <label>Prénom *</label>
            <input
              type="text"
              value={newUserData.first_name}
              onChange={(e) => setNewUserData({...newUserData, first_name: e.target.value})}
              placeholder="Saisir le prénom"
            />

            <label>Nom *</label>
            <input
              type="text"
              value={newUserData.last_name}
              onChange={(e) => setNewUserData({...newUserData, last_name: e.target.value})}
              placeholder="Saisir le nom"
            />

            <label>Rôle *</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
            >
              <option value="">— Sélectionner un rôle —</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>

            <label>Équipe</label>
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
            >
              <option value="">— Aucune équipe —</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>

            <div className="users-modal-buttons" style={{ marginTop: 16 }}>
              <button className="users-btn users-btn-save" onClick={handleAddUser}>
                Créer l'utilisateur
              </button>
              <button className="users-btn users-btn-cancel" onClick={closeAddUser}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation */}
      {viewingUser && (
        <div className="users-modal-overlay" onClick={closeView}>
          <div className="users-modal users-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="users-modal-header">
              <h2>
                {viewingUser.first_name && viewingUser.last_name ? 
                  `${viewingUser.first_name} ${viewingUser.last_name}` : 
                  viewingUser.username || 'Utilisateur'
                }
              </h2>
              <button className="users-modal-close" onClick={closeView}>
                ×
              </button>
            </div>
            
            <div className="users-modal-info">
              <p><strong>Email :</strong> {viewingUser.email || 'Non défini'}</p>
              <p><strong>Prénom :</strong> {viewingUser.first_name || 'Non défini'}</p>
              <p><strong>Nom :</strong> {viewingUser.last_name || 'Non défini'}</p>
              <p><strong>Rôle :</strong> {getRoleName(viewingUser)}</p>
              <p><strong>Équipe :</strong> {viewingUser.team ? viewingUser.team.name : 'Aucune équipe'}</p>
            </div>

            <div className="users-modal-buttons" style={{ marginTop: 20 }}>
              <button className="users-btn users-btn-edit" onClick={() => {
                closeView();
                openEdit(viewingUser);
              }}>
                Modifier cet utilisateur
              </button>
              <button className="users-btn users-btn-cancel" onClick={closeView}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de modification */}
      {editingUser && (
        <div className="users-modal-overlay" onClick={closeEdit}>
          <div className="users-modal users-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="users-modal-header">
              <h2>Modifier l'utilisateur</h2>
              <button className="users-modal-close" onClick={closeEdit}>
                ×
              </button>
            </div>

            <label>Email *</label>
            <input
              type="email"
              value={editingUser.email}
              onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
            />

            <label>Prénom *</label>
            <input
              type="text"
              value={editingUser.first_name || ''}
              onChange={(e) => setEditingUser({ ...editingUser, first_name: e.target.value })}
            />

            <label>Nom *</label>
            <input
              type="text"
              value={editingUser.last_name || ''}
              onChange={(e) => setEditingUser({ ...editingUser, last_name: e.target.value })}
            />

            <label>Rôle *</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
            >
              <option value="">— Sélectionner un rôle —</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>

            <label>Équipe</label>
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
            >
              <option value="">— Aucune équipe —</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>

            <div className="users-modal-buttons" style={{ marginTop: 16 }}>
              <button className="users-btn users-btn-save" onClick={handleSave}>
                Valider
              </button>
              <button className="users-btn users-btn-cancel" onClick={closeEdit}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de suppression */}
      {deletingUser && (
        <div className="users-modal-overlay" onClick={cancelDelete}>
          <div className="users-modal users-delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              Êtes-vous sûr de vouloir supprimer{" "}
              <strong>
                {deletingUser.first_name && deletingUser.last_name ? 
                  `${deletingUser.first_name} ${deletingUser.last_name}` : 
                  deletingUser.email
                }
              </strong> ?
            </h2>
            <div className="users-modal-buttons">
              <button className="users-btn users-btn-delete" onClick={confirmDelete}>
                Supprimer
              </button>
              <button className="users-btn users-btn-cancel" onClick={cancelDelete}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal d'erreur */}
      {errorModal.show && (
        <div className="users-modal-overlay" onClick={closeErrorModal}>
          <div className="users-modal users-error-modal" onClick={(e) => e.stopPropagation()}>
            <div className="users-modal-header">
              <h2 style={{ color: '#dc3545' }}>{errorModal.title}</h2>
              <button className="users-modal-close" onClick={closeErrorModal}>
                ×
              </button>
            </div>
            <div className="users-modal-body" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px', color: '#dc3545' }}>⚠️</span>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>
                  {errorModal.message}
                </p>
              </div>
            </div>
            <div className="users-modal-buttons">
              <button className="users-btn users-btn-cancel" onClick={closeErrorModal}>
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
