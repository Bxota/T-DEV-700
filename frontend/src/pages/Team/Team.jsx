import React, { useState, useEffect } from 'react';
import './Team.css';
import { getAuthHeaders } from '../../api/auth';
import { useUser } from '../../context/UserContext';

const Team = () => {
  const { user } = useUser();
  const rawRole = user?.role;
  const roleName = (typeof rawRole === 'string' ? rawRole : rawRole?.name) || user?.roleName || '';
  const canManage = String(roleName).toLowerCase() === 'manager'; // 👈 manager = peut créer/modifier/supprimer

  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [viewingTeam, setViewingTeam] = useState(null);
  const [editingTeam, setEditingTeam] = useState(null);
  const [deletingTeam, setDeletingTeam] = useState(null);
  const [addingTeam, setAddingTeam] = useState(false);
  const [selectedMember, setSelectedMember] = useState('');
  const [tempMembers, setTempMembers] = useState([]);
  const [allEmployees, setAllEmployees] = useState([]);
  const [newTeamName, setNewTeamName] = useState('');
  const [errorModal, setErrorModal] = useState({ show: false, message: '', title: '' });
  const [addingMemberTeam, setAddingMemberTeam] = useState(null);

  // Récupération des données depuis l'API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const teamsResponse = await fetch('/api/teams/', { headers: getAuthHeaders() });
        if (!teamsResponse.ok) throw new Error(`Erreur teams: ${teamsResponse.status}`);

        const teamsData = await teamsResponse.json();
        const list = teamsData.teams || teamsData.results || teamsData || [];
        // Cloner pour éviter de muter l'original
        const cloned = Array.isArray(list) ? list.map(t => ({ ...t })) : [];
        // Charger les membres de chaque équipe
        for (let team of cloned) {
          const members = await getMembers(team.id);
          team.members = members ?? [];
        }
        setTeams(cloned);
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
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    setAddingTeam(true);
    setNewTeamName('');
    setTempMembers([]);
    setSelectedMember('');
    fetchAllUsers();
  };

  const closeAddTeam = () => {
    setAddingTeam(false);
    setNewTeamName('');
    setTempMembers([]);
    setSelectedMember('');
  };

  // Modal d'erreur
  const showErrorModal = (title, message) => setErrorModal({ show: true, title, message });
  const closeErrorModal = () => setErrorModal({ show: false, message: '', title: '' });

  const handleAddTeam = async () => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    if (!newTeamName.trim()) return showErrorModal('Erreur de validation', "Veuillez saisir un nom d'équipe");

    try {
      const response = await fetch('/api/teams/', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ name: newTeamName.trim(), team_id: null })
      });

      if (response.ok) {
        const responseData = await response.json();
        const newTeam = responseData.team || responseData;

        // Ajout des membres si sélectionnés
        if (tempMembers.length > 0) {
          try {
            for (const member of tempMembers) {
              if (typeof member === 'object' && member.id) {
                await fetch(`/api/users/teams/${newTeam.id}/`, {
                  method: 'POST',
                  headers: getAuthHeaders(),
                  body: JSON.stringify({ user_id: member.id })
                });
              }
            }
            newTeam.members = tempMembers;
          } catch (userError) {
            console.error("Erreur ajout utilisateurs:", userError);
            newTeam.members = [];
          }
        } else {
          newTeam.members = [];
        }

        setTeams(prev => [...prev, newTeam]);
        closeAddTeam();
      } else {
        let errorMessage = "Erreur lors de la création de l'équipe";
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
      showErrorModal('Erreur réseau', "Impossible de communiquer avec le serveur. Vérifiez votre connexion.");
    }
  };

  const getMembers = async (teamId) => {
    try {
      const response = await fetch(`/api/users/teams/${teamId}/`, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        return data.users;
      }
    } catch (err) {
      console.error('Erreur:', err);
    }
    return [];
  };

  const openView = (team) => setViewingTeam(team);

  const openEdit = (team) => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    setEditingTeam({ ...team });
    setTempMembers(Array.isArray(team.members) ? [...team.members] : []);
    setSelectedMember('');
    fetchAllUsers();
  };

  const closeEdit = () => {
    setEditingTeam(null);
    setTempMembers([]);
  };

  const handleSave = async () => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    try {
      const payload = { name: editingTeam.name, team_id: editingTeam.id };

      const response = await fetch(`/api/teams/${editingTeam.id}/`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const responseData = await response.json();

        // Diff membres (remove/add)
        const originalMemberIds = Array.isArray(editingTeam.members)
          ? editingTeam.members.map(m => (typeof m === 'object' ? m.id : m))
          : [];
        const currentMemberIds = tempMembers.map(m => (typeof m === 'object' ? m.id : m));

        const membersToRemove = (editingTeam.members || []).filter(member => {
          const memberId = typeof member === 'object' ? member.id : member;
          return !currentMemberIds.includes(memberId);
        });

        const membersToAdd = tempMembers.filter(member => {
          const memberId = typeof member === 'object' ? member.id : member;
          return !originalMemberIds.includes(memberId);
        });

        // Supprimer
        for (const member of membersToRemove) {
          if (typeof member === 'object' && member.id) {
            await fetch(`/api/users/teams/${editingTeam.id}/`, {
              method: 'DELETE',
              headers: getAuthHeaders(),
              body: JSON.stringify({ user_id: member.id })
            });
          }
        }

        // Ajouter
        for (const member of membersToAdd) {
          if (typeof member === 'object' && member.id) {
            await fetch(`/api/users/teams/${editingTeam.id}/`, {
              method: 'POST',
              headers: getAuthHeaders(),
              body: JSON.stringify({ user_id: member.id })
            });
          }
        }

        const updatedTeam = {
          ...editingTeam,
          name: responseData.new_name || editingTeam.name,
          members: tempMembers
        };

        setTeams(prev => prev.map(team => (team.id === editingTeam.id ? updatedTeam : team)));
        if (viewingTeam?.id === editingTeam.id) setViewingTeam(updatedTeam);
        closeEdit();
      } else {
        let errorMessage = "Erreur lors de la modification de l'équipe";
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
      showErrorModal('Erreur réseau', "Impossible de communiquer avec le serveur. Vérifiez votre connexion.");
    }
  };

  const addTempMember = () => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    if (!selectedMember) return;

    const userToAdd = allEmployees.find(
      u => u.id?.toString() === selectedMember || u.username === selectedMember
    );

    const isAlreadyAdded = tempMembers.some(member => {
      if (typeof member === 'object' && typeof userToAdd === 'object') return member.id === userToAdd.id;
      return member === selectedMember;
    });
    if (isAlreadyAdded) return;

    setTempMembers(prev => [...prev, userToAdd || selectedMember]);
    setSelectedMember('');
  };

  const removeTempMember = (index) => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    setTempMembers(prev => prev.filter((_, i) => i !== index));
  };

  const askDelete = (team) => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    setDeletingTeam(team);
  };
  const cancelDelete = () => setDeletingTeam(null);

  const confirmDelete = async () => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
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
        let errorMessage = "Erreur lors de la suppression de l'équipe";
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
      showErrorModal('Erreur réseau', "Impossible de communiquer avec le serveur. Vérifiez votre connexion.");
    }
  };

  const getAvailableMembers = () => {
    if (!allEmployees || allEmployees.length === 0) return [];
    if (addingTeam) {
      return allEmployees.filter(user =>
        !tempMembers.some(member =>
          typeof member === 'object' ? member.id === user.id : member === user.username || member === user.id
        )
      );
    }
    if (!editingTeam) return [];
    return allEmployees.filter(user =>
      !tempMembers.some(member =>
        typeof member === 'object' ? member.id === user.id : member === user.username || member === user.id
      )
    );
  };

  const openAddMember = (team) => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    setAddingMemberTeam(team);
    setTempMembers(Array.isArray(team.members) ? [...team.members] : []);
    setSelectedMember('');
    fetchAllUsers();
  };

  const closeAddMember = () => {
    setAddingMemberTeam(null);
    setTempMembers([]);
    setSelectedMember('');
  };

  const fetchAllUsers = async () => {
    try {
      const response = await fetch('/api/users/', { method: 'GET', headers: getAuthHeaders() });
      if (response.ok) {
        const usersData = await response.json();
        const usersList = Array.isArray(usersData)
          ? usersData
          : Array.isArray(usersData.users)
          ? usersData.users
          : [];
        setAllEmployees(usersList);
      } else {
        setAllEmployees([]);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des users:', error);
      setAllEmployees([]);
    }
  };

  const handleAddMemberToTeam = async () => {
    if (!canManage) return showErrorModal('Accès refusé', "Action réservée aux managers.");
    try {
      const payload = {
        name: addingMemberTeam.name,
        members: tempMembers,
        team_id: addingMemberTeam.id
      };

      const response = await fetch(`/api/teams/${addingMemberTeam.id}/`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const updatedTeam = { ...addingMemberTeam, members: tempMembers };
        setTeams(prev => prev.map(team => (team.id === addingMemberTeam.id ? updatedTeam : team)));
        if (viewingTeam?.id === addingMemberTeam.id) setViewingTeam(updatedTeam);
        closeAddMember();
        showSuccessMessage('Membres ajoutés avec succès !');
      } else {
        let errorMessage = "Erreur lors de l'ajout des membres";
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        showErrorModal("Erreur d'ajout de membres", errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', "Impossible de communiquer avec le serveur. Vérifiez votre connexion.");
    }
  };

  const getAvailableMembersForAdd = () => {
    if (!allEmployees || allEmployees.length === 0) return [];
    return allEmployees.filter(user =>
      !tempMembers.some(member =>
        typeof member === 'object' ? member.id === user.id : member === user.username || member === user.id
      )
    );
  };

  const showSuccessMessage = (message) => {
    alert(message);
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
          <button onClick={() => window.location.reload()}>Réessayer</button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Équipes</h1>
        <p className="page-description">
          {canManage ? "Gestion des équipes de l'entreprise" : "Liste des équipes (lecture seule)"}
        </p>
        {canManage && (
          <button className="add-button" onClick={openAddTeam}>
            + Ajouter une équipe
          </button>
        )}
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
                  {canManage ? (
                    <>
                      <button className="btn btn-edit" onClick={() => openEdit(team)}>
                        Modifier
                      </button>
                      <button className="btn btn-delete" onClick={() => askDelete(team)}>
                        Supprimer
                      </button>
                    </>
                  ) : (
                    <em className="muted-text">Lecture seule</em>
                  )}
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
      {addingTeam && canManage && (
        <div className="modal-overlay" onClick={closeAddTeam}>
          <div className="modal members-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Ajouter une équipe</h2>
              <button className="modal-close" onClick={closeAddTeam}>×</button>
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
              <select value={selectedMember} onChange={(e) => setSelectedMember(e.target.value)}>
                <option value="">— Sélectionner un membre —</option>
                {getAvailableMembers().map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.email}
                  </option>
                ))}
              </select>
              <button className="btn btn-save" onClick={addTempMember}>Ajouter</button>
            </div>

            <div className="members-list">
              {tempMembers.length === 0 ? (
                <p className="members-empty">Aucun membre sélectionné</p>
              ) : (
                tempMembers.map((m, i) => (
                  <div key={`add-member-${i}-${typeof m === 'object' ? m.id : m}`} className="member-item">
                    <span>
                      {typeof m === 'object'
                        ? (m.first_name && m.last_name ? `${m.first_name} ${m.last_name}` : m.username || m.name || m.email || `Utilisateur ${m.id}`)
                        : m}
                      {typeof m === 'object' && m.first_name && m.last_name && m.email && (
                        <small style={{ color: '#666', marginLeft: '10px' }}>({m.email})</small>
                      )}
                    </span>
                    <button className="btn btn-delete btn-sm" onClick={() => removeTempMember(i)}>
                      Supprimer
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="modal-buttons" style={{ marginTop: 16 }}>
              <button className="btn btn-save" onClick={handleAddTeam}>Créer l'équipe</button>
              <button className="btn btn-cancel" onClick={closeAddTeam}>Annuler</button>
            </div>
          </div>
        </div>
      )}

      {viewingTeam && (
        <div className="modal-overlay" onClick={() => setViewingTeam(null)}>
          <div className="modal members-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{viewingTeam.name}</h2>
              <button className="modal-close" onClick={() => setViewingTeam(null)}>×</button>
            </div>

            <div className="modal-info" style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
                <strong>Nombre de membres :</strong> {viewingTeam.members ? viewingTeam.members.length : 0}
              </p>
            </div>

            <div className="members-list">
              <h3 style={{ fontSize: '16px', marginBottom: '10px' }}>Membres de l'équipe</h3>
              {(!viewingTeam.members || viewingTeam.members.length === 0) ? (
                <p className="members-empty">Aucun membre</p>
              ) : (
                viewingTeam.members.map((m, i) => (
                  <div key={`view-member-${i}-${typeof m === 'object' ? m.id : m}`} className="member-item view-only">
                    <span>
                      {typeof m === 'object'
                        ? (m.first_name && m.last_name ? `${m.first_name} ${m.last_name}` : m.username || m.name || m.email || `Utilisateur ${m.id}`)
                        : m}
                      {typeof m === 'object' && m.first_name && m.last_name && m.email && (
                        <small style={{ color: '#666', marginLeft: '10px' }}>({m.email})</small>
                      )}
                    </span>
                  </div>
                ))
              )}
            </div>

            <div className="modal-buttons" style={{ marginTop: 20 }}>
              {canManage && (
                <button className="btn btn-edit" onClick={() => { setViewingTeam(null); openEdit(viewingTeam); }}>
                  Modifier cette équipe
                </button>
              )}
              <button className="btn btn-cancel" onClick={() => setViewingTeam(null)}>Fermer</button>
            </div>
          </div>
        </div>
      )}

      {editingTeam && canManage && (
        <div className="modal-overlay" onClick={closeEdit}>
          <div className="modal members-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Modifier {editingTeam.name}</h2>
              <button className="modal-close" onClick={closeEdit}>×</button>
            </div>

            <label>Nom de l'équipe</label>
            <input
              type="text"
              value={editingTeam.name}
              onChange={(e) => setEditingTeam({ ...editingTeam, name: e.target.value })}
            />

            <div className="member-add-row">
              <select value={selectedMember} onChange={(e) => setSelectedMember(e.target.value)}>
                <option value="">— Sélectionner un membre —</option>
                {getAvailableMembers().map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.email}
                  </option>
                ))}
              </select>
              <button className="btn btn-save" onClick={addTempMember}>Ajouter</button>
            </div>

            <div className="members-list">
              {tempMembers.length === 0 ? (
                <p className="members-empty">Aucun membre</p>
              ) : (
                tempMembers.map((m, i) => (
                  <div key={`edit-member-${i}-${typeof m === 'object' ? m.id : m}`} className="member-item">
                    <span>
                      {typeof m === 'object'
                        ? (m.first_name && m.last_name ? `${m.first_name} ${m.last_name}` : m.username || m.name || m.email || `Utilisateur ${m.id}`)
                        : m}
                      {typeof m === 'object' && m.first_name && m.last_name && m.email && (
                        <small style={{ color: '#666', marginLeft: '10px' }}>({m.email})</small>
                      )}
                    </span>
                    <button className="btn btn-delete btn-sm" onClick={() => removeTempMember(i)}>
                      Supprimer
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="modal-buttons" style={{ marginTop: 16 }}>
              <button className="btn btn-save" onClick={handleSave}>Valider</button>
              <button className="btn btn-cancel" onClick={closeEdit}>Annuler</button>
            </div>
          </div>
        </div>
      )}

      {deletingTeam && canManage && (
        <div className="modal-overlay" onClick={cancelDelete}>
          <div className="modal delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Êtes-vous sûr de vouloir supprimer <strong>{deletingTeam.name}</strong> ?</h2>
            <div className="modal-buttons">
              <button className="btn btn-delete" onClick={confirmDelete}>Supprimer</button>
              <button className="btn btn-cancel" onClick={cancelDelete}>Annuler</button>
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
              <button className="modal-close" onClick={closeErrorModal}>×</button>
            </div>
            <div className="modal-body" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px', color: '#dc3545' }}>⚠️</span>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{errorModal.message}</p>
              </div>
            </div>
            <div className="modal-buttons">
              <button className="btn btn-cancel" onClick={closeErrorModal}>OK</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Team;
