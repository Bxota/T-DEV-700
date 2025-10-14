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
  const [selectedTeam, setSelectedTeam] = useState("");
  const [teams, setTeams] = useState([]); // Initialisé en tant que tableau vide
  const [loadingTeams, setLoadingTeams] = useState(false);
  const [teamsError, setTeamsError] = useState(null);

  const toggleStats = () => {
    setShowStats(!showStats);
  };

  useEffect(() => {
    const controller = new AbortController();

    const fetchTeams = async () => {
      setLoadingTeams(true);
      setTeamsError(null);
      try {
        const res = await fetch("/api/teams", { 
          signal: controller.signal, 
          headers: getAuthHeaders()
        });
        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
        const data = await res.json();
        
        // Vérifiez que data est bien un tableau
        if (Array.isArray(data.teams)) {
          setTeams(data.teams);
          setSelectedTeam(data.teams.length > 0 ? data.teams[0].id : ""); // Sélectionne la première équipe si disponible
        } else {
          console.error("La réponse de l'API n'est pas un tableau:", data);
          setTeams([]); // Force un tableau vide si la réponse n'est pas un tableau
          setTeamsError("Format de données incorrect");
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          setTeamsError(err.message || "Erreur lors de la récupération des équipes");
          setTeams([]); // Vide le tableau des équipes en cas d'erreur
          setSelectedTeam(""); // Remet la sélection à vide
        }
      } finally {
        setLoadingTeams(false);
      }
    };

    fetchTeams();
    return () => controller.abort();
  }, []);

  const handleTeamChange = (e) => {
    setSelectedTeam(e.target.value);
  };

  return (
    <div className="manager-container">
      <div className="manager-card">
        <select 
          className="team-selector"
          value={selectedTeam}
          onChange={handleTeamChange}
          disabled={loadingTeams || teamsError}
        >
          {!teamsError && Array.isArray(teams) && teams.map(team => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
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
        </div>
        
        <Planning 
          selectedTeam={selectedTeam} 
          selectedDate={selectedDate}
          teams={teams}
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
        <TeamStats selectedTeam={selectedTeam}/>
      </div>
    </div>
  );
}
