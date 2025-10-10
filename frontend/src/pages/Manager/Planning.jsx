import React, { useState, useEffect } from "react";
import "react-datepicker/dist/react-datepicker.css";

export default function Planning({ selectedTeam, selectedDate, teams }) {
  // Changez le nombre ici pour avoir plus de colonnes
  const hours = Array.from({ length: 15 }, (_, i) => 7 + i); // 15 colonnes au lieu de 11
  const [currentTime, setCurrentTime] = useState(new Date());

  // Met à jour l'heure actuelle chaque minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Met à jour chaque minute

    return () => clearInterval(timer);
  }, []);

  // Calcule la position de la ligne d'heure actuelle
  const getCurrentTimePosition = () => {
    const now = currentTime;
    const currentHour = now.getHours();
    const currentMinutes = now.getMinutes();
    
    // Vérifie si l'heure actuelle est dans la plage affichée (8h-22h)
    if (currentHour < 8 || currentHour >= 23) {
      return null; // Pas d'affichage si en dehors des heures
    }

    // Calcule le pourcentage de position
    const startHour = 6; // 7h moins 1 pour le début de la plage
    const totalMinutesFromStart = (currentHour - startHour) * 60 + currentMinutes;
    const totalMinutesInSchedule = 15 * 60; // 15 heures * 60 minutes
    const position = (totalMinutesFromStart / totalMinutesInSchedule) * 100;

    return Math.min(Math.max(position, 0), 100); // Limite entre 0 et 100%
  };

  const timeLinePosition = getCurrentTimePosition();

  // Trouve l'équipe sélectionnée dans le tableau teams
  const currentTeam = teams.find(team => team.id === selectedTeam);

  // Utilisation des props
  // console.log("Équipe sélectionnée:", selectedTeam);
  // console.log("Date sélectionnée:", selectedDate);
  // console.log("Toutes les équipes:", teams);
  // console.log("Équipe actuelle:", currentTeam);

  return (
    <>
      <div className="scheduler-container">
        <div className="scheduler-hour">
          {hours.map(hour => (
              <p key={hour} className="hour-header">
                {hours.indexOf(hour) === 14 ? '' : (hour < 10 ? '0' : '') + hour}
              </p>
          ))}
        </div>
        
        <div className="scheduler-body">
          {/* Ligne d'heure actuelle */}
          {timeLinePosition !== null && (
            <div 
              className="current-time-line"
              style={{ left: `${timeLinePosition}%` }}
            >
              <div className="current-time-indicator">
                {currentTime.getHours()}:{currentTime.getMinutes().toString().padStart(2, '0')}
              </div>
            </div>
          )}
          
          {hours.map(hour => (
            <div key={hour} className="time-slot">
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
