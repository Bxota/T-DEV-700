import { useState } from "react";
import Planning from "./Planning";
import TeamStats from "./TeamStats";
import PersonalInfo from "./PersonalInfo";
import "./css/Manager.css";

export default function Manager() {
  const [showStats, setShowStats] = useState(false);

  const toggleStats = () => {
    setShowStats(!showStats);
  };

  return (
    <div className="manager-container">
      
      <Planning />
      <PersonalInfo />
      
      {/* Flèche pour afficher/masquer les stats */}
      <button 
        className={`stats-arrow-btn ${showStats ? 'active' : ''}`}
        onClick={toggleStats}
        title={showStats ? 'Masquer les statistiques' : 'Afficher les statistiques'}
      >
        <span className="arrow-icon">></span>
      </button>

      {/* Panneau des statistiques */}
      <div className={`stats-panel ${showStats ? 'visible' : 'hidden'}`}>
        <TeamStats />
      </div>
    </div>
  );
}
