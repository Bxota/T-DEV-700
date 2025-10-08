export default function TeamStats() {
  const teamData = { 
    team: "Mon Équipe", 
    performance: 92, 
    tasks: 45, 
    absenceRate: 7,
    members: 14,
    completedTasks: 41
  };

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
          <h3 className="team-name-single">{teamData.team}</h3>
          <div className="team-members-badge">{teamData.members} membres</div>
        </div>

        {/* Métriques principales */}
        <div className="metrics-grid">
          {/* Performance */}
          <div className="metric-card">
            <div className="metric-header">
              <h4>Performance</h4>
              <span className="metric-value">{teamData.performance}%</span>
            </div>
            <ProgressBar 
              percentage={teamData.performance}
              color={performanceColor}
              label="Efficacité générale"
            />
          </div>

          {/* Taux d'absence */}
          <div className="metric-card">
            <div className="metric-header">
              <h4>Taux d'absence</h4>
              <span className="metric-value">{teamData.absenceRate}%</span>
            </div>
            <div className="absence-display">
              <CircleProgress percentage={teamData.absenceRate} />
            </div>
          </div>

          {/* Tâches */}
          <div className="metric-card">
            <div className="metric-header">
              <h4>Tâches réalisées</h4>
              <span className="metric-value">{teamData.completedTasks}/{teamData.tasks}</span>
            </div>
            <ProgressBar 
              percentage={taskCompletionRate}
              color="#17a2b8"
              label="Taux de completion"
            />
          </div>
        </div>
    </>
  );
}
