import React, {useState, useEffect} from "react";
import { getAuthHeaders } from "../../api/auth";

export default function TeamStats({ selectedTeam }) {

  const [teamData, setTeamData] = useState({});
  
  const fetchTeamReports = async (selectedTeam) => {
    if (!selectedTeam) return;
    console.log("selectedTeam ?", selectedTeam);
    try {
      const response = await fetch(`/api/teams/${selectedTeam}/reports/`,
        { headers: getAuthHeaders() }
      );
      if (response.ok) {
        const data = await response.json();
        setTeamData(data);
        console.log("data ?", data);
        // Pour les tests, on peut simuler des données ici
        // setTeamData({
        //       "members": 3,
        //       "total_shifts": 10,
        //       "total_with_checkin": 8,
        //       "lateness_count": 2,
        //       "lateness_rate": 25.0,
        //       "absences_count": 1,
        //       "absences_rate": 10.0,
        //       "total_worked_minutes": 177,
        //       "team_name": "test2",
        //       "team_id": 2
        //   });

      }
    } catch (error) {
      console.error('Error fetching team reports:', error);
    }
  };
  useEffect(() => {

    fetchTeamReports(selectedTeam);
  }, [selectedTeam]);

  // Composant pour le cercle de progression
  const CircleProgress = ({ percentage, size = 80, strokeWidth = 6 }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = `${circumference} ${circumference}`;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    const getColor = (rate) => {
      if (rate <= 5) return "#28a745";
      if (rate <= 10) return "#ffc107"; 
      if (rate <= 15) return "#fd7e14";
      return "#dc3545";
    };

    return (
      <div className="circle-progress" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="circle-progress-svg">
          <circle
            className="circle-progress-bg"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
          />
          <circle
            className="circle-progress-fill"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
            style={{ stroke: getColor(percentage) }}
          />
        </svg>
        <div className="circle-progress-text">
          <span className="percentage">{percentage}%</span>
        </div>
      </div>
    );
  };

  // Composant pour la barre de progression
  const ProgressBar = ({ percentage, color = "#007bff", label }) => {
    return (
      <div className="progress-container">
        <div className="progress-info">
          <span className="progress-label">{label}</span>
          <span className="progress-percentage">{percentage}%</span>
        </div>
        <div className="progress-bar-container">
          <div 
            className="progress-bar-fill"
            style={{ 
              width: `${percentage}%`,
              backgroundColor: color
            }}
          ></div>
        </div>
      </div>
    );
  };

  const performanceColor = teamData.performance >= 90 ? "#28a745" : 
                          teamData.performance >= 80 ? "#ffc107" : "#dc3545";
  
  const taskCompletionRate = Math.round((teamData.completedTasks / teamData.tasks) * 100);

  return (
    <>
        {/* En-tête de l'équipe */}
        <div className="team-header-single">
          <h3 className="team-name-single">{teamData.team_name}</h3>
          <div className="team-members-badge">{teamData.members} membres</div>
        </div>

        {/* Métriques principales */}
        <div className="metrics-grid">

          {/* Taux d'absence */}
          <div className="metric-card">
            <div className="metric-header">
              <h4>Taux d'absence</h4>
              <span className="metric-value">{teamData.absences_rate}%</span>
            </div>
            <div className="absence-display">
              <CircleProgress percentage={teamData.absences_rate} />
            </div>
          </div>

          {/* Tâches */}
          <div className="metric-card">
            <div className="metric-header">
              <h4>Nombre d'heures travaillées</h4>
            <span className="metric-value">{teamData.total_worked_minutes/60}h</span>
            </div>
            <div className="metric-header">
              <h4>quantité de retard</h4>
              <span className="metric-value"> {teamData.lateness_count ? `${teamData.lateness_count} / ${teamData.lateness_count * 100 / teamData.lateness_rate}` : 0}</span>
            </div>
            <ProgressBar 
              percentage={teamData.lateness_rate}
              color="#17a2b8"
              label="Taux de retard"
              />

          </div>

        </div>
    </>
  );
}
