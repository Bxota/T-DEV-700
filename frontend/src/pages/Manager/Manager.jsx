import { useState, useEffect, useRef } from "react";
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
  const [panelHeight, setPanelHeight] = useState(0);
  const panelRef = useRef(null);

  const toggleStats = () => {
    setShowStats(!showStats);
  };

  // Calcule la hauteur du stats-panel
  useEffect(() => {
    const calculateHeight = () => {
      if (panelRef.current) {
        const height = panelRef.current.scrollHeight;
        setPanelHeight(height);
      }
    };

    calculateHeight();
    window.addEventListener('resize', calculateHeight);
    return () => window.removeEventListener('resize', calculateHeight);
  }, [showStats]);

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
        
        <div className="datepicker-container">
          <button
            className="date-nav-btn prev"
            onClick={() => {
              const newDate = new Date(selectedDate);
              newDate.setDate(newDate.getDate() - 1);
              setSelectedDate(newDate);
            }}
            title="Date précédente"
          >
            ‹
          </button>
          
          <DatePicker
            selected={selectedDate}
            onChange={date => setSelectedDate(date)}
            dateFormat="dd/MM/yyyy"
            className="datepicker-input"
          />
          
          <button
            className="date-nav-btn next"
            onClick={() => {
              const newDate = new Date(selectedDate);
              newDate.setDate(newDate.getDate() + 1);
              setSelectedDate(newDate);
            }}
            title="Date suivante"
          >
            ›
          </button>
        </div>
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
        style={showStats ? { '--panel-height': `${panelHeight}px` } : {}}
      >
        <span className="arrow-icon">&gt;</span>
      </button>

      {/* Panneau des statistiques */}
      <div 
        ref={panelRef}
        className={`stats-panel ${showStats ? 'visible' : 'hidden'}`}
      >
        <TeamStats selectedTeam={team?.id}/>
      </div>
    </div>
  );
}
