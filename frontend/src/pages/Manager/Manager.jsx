import { useState } from "react";
import Planning from "./Planning";
import TeamStats from "./TeamStats";
import PersonalInfo from "./PersonalInfo";
import "./css/Manager.css";
import DatePicker from "react-datepicker";


export default function Manager() {
  const [showStats, setShowStats] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());

  const toggleStats = () => {
    setShowStats(!showStats);
  };

  

  return (
    <div className="manager-container">
      <div className="manager-card">
        <select className="team-selector">
          <option value="">Sélectionnez une équipe</option>
          <option value="equipe1">Equipe 1</option>
          <option value="equipe2">Equipe 2</option>
          <option value="equipe3">Equipe 3</option>
        </select> 
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
        <Planning />
      </div>
      <PersonalInfo />
      
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
        <TeamStats />
      </div>
    </div>
  );
}
