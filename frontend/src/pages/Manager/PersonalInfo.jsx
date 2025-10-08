import React from "react";
import "./css/PersonalInfo.css";

export default function PersonalInfo() {
  const manager = {
    firstName: "Jean",
    lastName: "Dupont",
    position: "Chef d'équipe",
    email: "jean.dupont@entreprise.com",
    phone: "06 23 45 67 89",
  };

  // Horaires de la journée sélectionnée
  const todaySchedule = {
    date: new Date().toLocaleDateString('fr-FR', { 
      weekday: 'long', 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric' 
    }),
    workStart: "08:00",
    workEnd: "18:00",
    breaks: [
      { start: "12:00", end: "13:00", type: "Déjeuner" },
      { start: "15:30", end: "15:45", type: "Pause" }
    ],
    meetings: [
      { start: "09:00", end: "10:30", title: "Réunion équipe" },
      { start: "14:00", end: "15:00", title: "Point client" }
    ]
  };

  // Statistiques personnelles
  const personalStats = {
    tasksCompleted: 12,
    totalTasks: 15,
    hoursWorked: 7.5,
    efficiency: 85,
    weeklyGoal: 40
  };

  const completionRate = Math.round((personalStats.tasksCompleted / personalStats.totalTasks) * 100);

  return (
    <div className="personal-info-sidebar">
      {/* Section 1: Nom et Prénom */}
      <div className="personal-identity">
        <div className="identity-info">
          <h2 className="full-name">
            {manager.firstName} {manager.lastName}
          </h2>
          <p className="position">{manager.position}</p>
        </div>
      </div>

      {/* Section 2: Horaires de la journée */}
      <div className="daily-schedule">
        <h3 className="section-title">Horaires du jour</h3>
        <div className="schedule-date">{todaySchedule.date}</div>
        
        <div className="work-hours">
          <div className="work-time">
            <span className="time-label">Début:</span>
            <span className="time-value">{todaySchedule.workStart}</span>
          </div>
          <div className="work-time">
            <span className="time-label">Fin:</span>
            <span className="time-value">{todaySchedule.workEnd}</span>
          </div>
        </div>

        <div className="schedule-events">
          <h4 className="events-title">Événements</h4>
          {todaySchedule.breaks.map((breakTime, index) => (
            <div key={index} className="schedule-item break">
              <span className="event-time">{breakTime.start} - {breakTime.end}</span>
              <span className="event-title">{breakTime.type}</span>
            </div>
          ))}
          {todaySchedule.meetings.map((meeting, index) => (
            <div key={index} className="schedule-item meeting">
              <span className="event-time">{meeting.start} - {meeting.end}</span>
              <span className="event-title">{meeting.title}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Section 3: Statistiques personnelles */}
      <div className="personal-stats">
        <h3 className="section-title">Mes statistiques</h3>
        
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-number">{personalStats.tasksCompleted}</div>
            <div className="stat-label">Tâches terminées</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{personalStats.hoursWorked}h</div>
            <div className="stat-label">Heures travaillées</div>
          </div>
        </div>

        <div className="progress-section">
          <div className="progress-item">
            <div className="progress-header">
              <span className="progress-label">Progression des tâches</span>
              <span className="progress-percentage">{completionRate}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${completionRate}%` }}
              ></div>
            </div>
          </div>

          <div className="progress-item">
            <div className="progress-header">
              <span className="progress-label">Efficacité</span>
              <span className="progress-percentage">{personalStats.efficiency}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill efficiency"
                style={{ width: `${personalStats.efficiency}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="weekly-summary">
          <h4 className="summary-title">Résumé hebdomadaire</h4>
          <div className="summary-stat">
            <span>Objectif: {personalStats.weeklyGoal}h</span>
            <span>Réalisé: {personalStats.hoursWorked * 5}h</span>
          </div>
        </div>
      </div>
    </div>
  );
}
