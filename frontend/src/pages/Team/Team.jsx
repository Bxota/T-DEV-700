import React, { useState, useEffect } from 'react';
import './Team.css';
import { getAuthHeaders } from '../../api/auth';

const Team = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [viewingTeam, setViewingTeam] = useState(null);
  const [editingTeam, setEditingTeam] = useState(null);
  const [deletingTeam, setDeletingTeam] = useState(null);
  const [addingTeam, setAddingTeam] = useState(false); // Nouvel état pour la modal d'ajout
  const [selectedMember, setSelectedMember] = useState('');
  const [tempMembers, setTempMembers] = useState([]);
  const [allEmployees, setAllEmployees] = useState([]);
  const [newTeamName, setNewTeamName] = useState(''); // État pour le nom de la nouvelle équipe
  const [errorModal, setErrorModal] = useState({ show: false, message: '', title: '' }); // Nouvel état pour la modal d'erreur

  // Récupération des données depuis l'API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Récupération des équipes
        const teamsResponse = await fetch('/api/teams/', {
          headers: getAuthHeaders()
        });
        
        if (!teamsResponse.ok) {
          throw new Error(`Erreur teams: ${teamsResponse.status}`);
        }
        
        const teamsData = await teamsResponse.json();
        setTeams(teamsData.teams);
        
      } catch (err) {
        console.error('Erreur lors de la récupération des données:', err);
        setError(err.message);
        setTeams([]);
        setAllEmployees([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const openAddTeam = () => {
    setAddingTeam(true);
    setNewTeamName('');
    setTempMembers([]);
    setSelectedMember('');
  };

  const closeAddTeam = () => {
    setAddingTeam(false);
    setNewTeamName('');
    setTempMembers([]);
    setSelectedMember('');
  };

  // Fonction pour afficher la modal d'erreur
  const showErrorModal = (title, message) => {
    setErrorModal({ show: true, title, message });
  };

  const closeErrorModal = () => {
    setErrorModal({ show: false, message: '', title: '' });
  };

  const handleAddTeam = async () => {
    if (!newTeamName.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un nom d\'équipe');
      return;
    }
    
    try {
      const response = await fetch('/api/teams/', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ 
          name: newTeamName.trim(), 
          members: tempMembers,
          team_id: null
        })
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Nouvelle équipe créée:', responseData);
        
        const newTeam = responseData.team || responseData;
        setTeams(prev => [...prev, newTeam]);
        closeAddTeam(); // Fermer la modal après création
      } else {
        // Récupérer le message d'erreur de l'API
        let errorMessage = 'Erreur lors de la création de l\'équipe';
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

  const openView = (team) => setViewingTeam(team);
  const closeView = () => setViewingTeam(null);

  const openEdit = (team) => {
    setEditingTeam({ ...team });
    setTempMembers([...team.members]); // copie temporaire
    setSelectedMember('');
  };
  const closeEdit = () => {
    setEditingTeam(null);
    setTempMembers([]);
  };

  const handleSave = async () => {
    try {
      const payload = { 
        name: editingTeam.name, 
        members: tempMembers,
        team_id: editingTeam.id
      };
      
      console.log('Données envoyées:', payload); // Debug
      
      const response = await fetch(`/api/teams/${editingTeam.id}/`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Réponse de l\'API:', responseData); // Debug

        const updatedTeam = {
          ...editingTeam,
          name: responseData.new_name || editingTeam.name,
          members: tempMembers
        };

        setTeams(prev => prev.map(team => 
          team.id === editingTeam.id ? updatedTeam : team
        ));

        // Mettre à jour aussi viewingTeam si c'est la même équipe
        if (viewingTeam?.id === editingTeam.id) {
          setViewingTeam(updatedTeam);
        }

        closeEdit();
      } else {
        // Récupérer le message d'erreur de l'API
        let errorMessage = 'Erreur lors de la modification de l\'équipe';
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

  const addTempMember = () => {
    if (!selectedMember || tempMembers.includes(selectedMember)) return;
    setTempMembers((prev) => [...prev, selectedMember]);
    setSelectedMember('');
  };

  const removeTempMember = (index) => {
    setTempMembers((prev) => prev.filter((_, i) => i !== index));
  };

  const askDelete = (team) => setDeletingTeam(team);
  const cancelDelete = () => setDeletingTeam(null);
  
  const confirmDelete = async () => {
    try {
      const response = await fetch(`/api/teams/${deletingTeam.id}/`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        setTeams(prev => prev.filter(t => t.id !== deletingTeam.id));
        if (viewingTeam?.id === deletingTeam.id) setViewingTeam(null);
        if (editingTeam?.id === deletingTeam.id) setEditingTeam(null);
        setDeletingTeam(null);
      } else {
        // Récupérer le message d'erreur de l'API
        let errorMessage = 'Erreur lors de la suppression de l\'équipe';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        
        setDeletingTeam(null);
        showErrorModal('Erreur de suppression', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      setDeletingTeam(null);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  const getAvailableMembers = () => {
    if (!editingTeam) return [];
    return allEmployees.filter((user) => 
      !tempMembers.some(member => 
        typeof member === 'object' ? member.id === user.id : member === user.username
      )
    );
  };

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <p>Chargement des équipes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
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
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Équipes</h1>
        <p className="page-description">Gestion des équipes de l'entreprise</p>
        <button className="add-button" onClick={openAddTeam}>
          + Ajouter une équipe
        </button>
      </div>

      <div className="team-table-container">
        <table className="team-table">
          <thead>
            <tr>
              <th>Nom de l'équipe</th>
              <th>Nombre de membres</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id} onClick={() => openView(team)} style={{ cursor: 'pointer' }}>
                <td>{team.name || 'Nom non défini'}</td>
                <td>{team.members ? team.members.length : 0}</td>
                <td className="actions-cell" onClick={(e) => e.stopPropagation()}>
                  <button className="btn btn-edit" onClick={() => openEdit(team)}>
                    Modifier
                  </button>
                  <button className="btn btn-delete" onClick={() => askDelete(team)}>
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
            {teams.length === 0 && !loading && (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                  {error ? 'Erreur lors du chargement des équipes' : 'Aucune équipe enregistrée'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal pour ajouter une équipe */}
      {addingTeam && (
        <div className="modal-overlay" onClick={closeAddTeam}>
          <div className="modal members-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Ajouter une équipe</h2>
              <button className="modal-close" onClick={closeAddTeam}>
                ×
              </button>
            </div>

            <label>Nom de l'équipe</label>
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Saisir le nom de l'équipe"
              autoFocus
            />

            <div className="member-add-row">
              <select
                value={selectedMember}
                onChange={(e) => setSelectedMember(e.target.value)}
              >
                <option value="">— Sélectionner un membre —</option>
                {getAvailableMembers().map((user) => (
                  <option key={user.id || user.username} value={user.username || user.id}>
                    {user.username || user} {user.email && `(${user.email})`}
                  </option>
                ))}
              </select>
              <button className="btn btn-save" onClick={addTempMember}>
                Ajouter
              </button>
            </div>

            <div className="members-list">
              {tempMembers.length === 0 ? (
                <p className="members-empty">Aucun membre sélectionné</p>
              ) : (
                tempMembers.map((m, i) => (
                  <div key={`add-member-${i}-${typeof m === 'object' ? m.id : m}`} className="member-item">
                    <span>{typeof m === 'object' ? m.username : m}</span>
                    <button className="btn btn-delete btn-sm" onClick={() => removeTempMember(i)}>
                      Supprimer
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="modal-buttons" style={{ marginTop: 16 }}>
              <button className="btn btn-save" onClick={handleAddTeam}>
                Créer l'équipe
              </button>
              <button className="btn btn-cancel" onClick={closeAddTeam}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {viewingTeam && (
        <div className="modal-overlay" onClick={closeView}>
          <div className="modal members-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{viewingTeam.name}</h2>
              <button className="modal-close" onClick={closeView}>
                ×
              </button>
            </div>
            <div className="members-list">
              {(!viewingTeam.members || viewingTeam.members.length === 0) ? (
                <p className="members-empty">Aucun membre</p>
              ) : (
                viewingTeam.members.map((m, i) => (
                  <div key={`view-member-${i}-${typeof m === 'object' ? m.id : m}`} className="member-item">
                    <span>{typeof m === 'object' ? m.username : m}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {editingTeam && (
        <div className="modal-overlay" onClick={closeEdit}>
          <div className="modal members-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Modifier {editingTeam.name}</h2>
              <button className="modal-close" onClick={closeEdit}>
                ×
              </button>
            </div>

            <label>Nom de l'équipe</label>
            <input
              type="text"
              value={editingTeam.name}
              onChange={(e) => setEditingTeam({ ...editingTeam, name: e.target.value })}
            />

            <div className="member-add-row">
              <select
                value={selectedMember}
                onChange={(e) => setSelectedMember(e.target.value)}
              >
                <option value="">— Sélectionner un membre —</option>
                {getAvailableMembers().map((user) => (
                  <option key={user.id || user.username} value={user.username || user.id}>
                    {user.username || user} {user.email && `(${user.email})`}
                  </option>
                ))}
              </select>
              <button className="btn btn-save" onClick={addTempMember}>
                Ajouter
              </button>
            </div>

            <div className="members-list">
              {tempMembers.length === 0 ? (
                <p className="members-empty">Aucun membre</p>
              ) : (
                tempMembers.map((m, i) => (
                  <div key={`edit-member-${i}-${typeof m === 'object' ? m.id : m}`} className="member-item">
                    <span>{typeof m === 'object' ? m.username : m}</span>
                    <button className="btn btn-delete btn-sm" onClick={() => removeTempMember(i)}>
                      Supprimer
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="modal-buttons" style={{ marginTop: 16 }}>
              <button className="btn btn-save" onClick={handleSave}>
                Valider
              </button>
              <button className="btn btn-cancel" onClick={closeEdit}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingTeam && (
        <div className="modal-overlay" onClick={cancelDelete}>
          <div className="modal delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              Êtes-vous sûr de vouloir supprimer <strong>{deletingTeam.name}</strong> ?
            </h2>
            <div className="modal-buttons">
              <button className="btn btn-delete" onClick={confirmDelete}>
                Supprimer
              </button>
              <button className="btn btn-cancel" onClick={cancelDelete}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal d'erreur */}
      {errorModal.show && (
        <div className="modal-overlay" onClick={closeErrorModal}>
          <div className="modal error-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 style={{ color: '#dc3545' }}>{errorModal.title}</h2>
              <button className="modal-close" onClick={closeErrorModal}>
                ×
              </button>
            </div>
            <div className="modal-body" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px', color: '#dc3545' }}>⚠️</span>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>
                  {errorModal.message}
                </p>
              </div>
            </div>
            <div className="modal-buttons">
              <button className="btn btn-cancel" onClick={closeErrorModal}>
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Team;
