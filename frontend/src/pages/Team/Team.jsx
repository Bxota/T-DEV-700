import React, { useState } from 'react';
import './Team.css';

const Team = () => {
  const allEmployees = [
    'Jean Dupont',
    'Marie Curie',
    'Luc Martin',
    'Alice Durand',
    'Bob Leroy',
    'Sophie Bernard',
    'Claire Petit',
    'Thomas Giraud',
  ];

  const [teams, setTeams] = useState([
    { id: 1, name: 'Équipe Alpha', members: ['Jean Dupont', 'Marie Curie'] },
    { id: 2, name: 'Équipe Bravo', members: ['Alice Durand', 'Bob Leroy'] },
  ]);

  const [viewingTeam, setViewingTeam] = useState(null);
  const [editingTeam, setEditingTeam] = useState(null);
  const [deletingTeam, setDeletingTeam] = useState(null);
  const [selectedMember, setSelectedMember] = useState('');
  const [tempMembers, setTempMembers] = useState([]);

  const handleAddTeam = () => {
    const name = prompt('Nom de la nouvelle équipe :');
    if (!name) return;
    setTeams((t) => [...t, { id: Date.now(), name, members: [] }]);
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

  const handleSave = () => {
    setTeams((prev) =>
      prev.map((t) =>
        t.id === editingTeam.id
          ? { ...t, name: editingTeam.name, members: tempMembers }
          : t
      )
    );
    if (viewingTeam?.id === editingTeam.id)
      setViewingTeam((v) => ({ ...v, name: editingTeam.name, members: tempMembers }));
    closeEdit();
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
  const confirmDelete = () => {
    setTeams((prev) => prev.filter((t) => t.id !== deletingTeam.id));
    if (viewingTeam?.id === deletingTeam.id) setViewingTeam(null);
    if (editingTeam?.id === deletingTeam.id) setEditingTeam(null);
    setDeletingTeam(null);
  };

  const getAvailableMembers = () => {
    if (!editingTeam) return [];
    return allEmployees.filter((emp) => !tempMembers.includes(emp));
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Équipes</h1>
        <p className="page-description">Gestion des équipes de l’entreprise</p>
        <button className="add-button" onClick={handleAddTeam}>
          + Ajouter une équipe
        </button>
      </div>

      <div className="team-table-container">
        <table className="team-table">
          <thead>
            <tr>
              <th>Nom de l’équipe</th>
              <th>Nombre de membres</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id} onClick={() => openView(team)} style={{ cursor: 'pointer' }}>
                <td>{team.name}</td>
                <td>{team.members.length}</td>
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
            {teams.length === 0 && (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                  Aucune équipe enregistrée
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

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
              {viewingTeam.members.length === 0 ? (
                <p className="members-empty">Aucun membre</p>
              ) : (
                viewingTeam.members.map((m, i) => (
                  <div key={i} className="member-item">
                    <span>{m}</span>
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

            <label>Nom de l’équipe</label>
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
                {getAvailableMembers().map((m, i) => (
                  <option key={i} value={m}>
                    {m}
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
                  <div key={i} className="member-item">
                    <span>{m}</span>
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
    </div>
  );
};

export default Team;
