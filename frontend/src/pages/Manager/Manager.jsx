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

  // Calcule la position de la ligne d'heure actuelle
  const getCurrentTimePosition = () => {
    const now = currentTime;
    const currentHour = now.getHours();
    const currentMinutes = now.getMinutes();
    
    // Vérifie si l'heure actuelle est dans la plage affichée (8h-22h pour 15 colonnes)
    if (currentHour < 8 || currentHour >= 23) {
      return null;
    }

    // Calcule le pourcentage de position
    const startHour = 8;
    const totalMinutesFromStart = (currentHour - startHour) * 60 + currentMinutes;
    const totalMinutesInSchedule = 15 * 60; // 15 heures * 60 minutes
    const position = (totalMinutesFromStart / totalMinutesInSchedule) * 100;

    return Math.min(Math.max(position, 0), 100);
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
