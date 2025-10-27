import { useState, useEffect } from "react";
import Planning from "./Planning";
import TeamStats from "./TeamStats";
import "./css/Manager.css";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { getAuthHeaders } from "../../api/auth";

export default function Manager() {
  const [showStats, setShowStats] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [team, setTeam] = useState(null);

  const toggleStats = () => {
    setShowStats(!showStats);
  };

  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user) {
      const parsedUser = JSON.parse(user);
      setTeam(parsedUser.team);
    }
  }, []);

  return (
    <div className="manager-container">
      <div className="manager-card">
        {team && (
          <div className="team-info">
            <h2>Équipe : {team.name}</h2>
          </div>
        )}
        
        <button
          className="add-member-btn"
          onClick={() => window.location.href = "/team"}
        >
          + Ajouter un membre
        </button>
        
        <DatePicker
          selected={selectedDate}
          onChange={date => setSelectedDate(date)}
          dateFormat="dd/MM/yyyy"
          className="datepicker-input"
        />
        </div>
        
        <Planning 
          selectedTeam={team?.id} 
          selectedDate={selectedDate}
          teams={team ? [team] : []}
        />
      
      
      {/* Flèche pour afficher/masquer les stats */}
      <button 
        className={`stats-arrow-btn ${showStats ? 'active' : ''}`}
        onClick={toggleStats}
        title={showStats ? 'Masquer les statistiques' : 'Afficher les statistiques'}
      >
        <span className="arrow-icon">&gt;</span>
      </button>

      {/* Panneau des statistiques */}
      <div className={`stats-panel ${showStats ? 'visible' : 'hidden'}`}>
        <TeamStats selectedTeam={team?.id}/>
      </div>
    </div>
  );
}
