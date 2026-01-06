import React, { useState, useEffect } from "react";
import "react-datepicker/dist/react-datepicker.css";
import { getAuthHeaders } from "../../api/auth";
import PersonalInfo from "./PersonalInfo";
import "./css/Planning.css";


export default function Planning({ selectedTeam, selectedDate, teams }) {
  // Affichage de 7h à 21h (15 colonnes)
  const hours = Array.from({ length: 15 }, (_, i) => 7 + i);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [usersError, setUsersError] = useState(null);
  const [shiftsByUser, setShiftsByUser] = useState({});
  const [loadingShifts, setLoadingShifts] = useState(false);
  const [shiftsError, setShiftsError] = useState(null);

  // Met à jour l'heure actuelle chaque minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Met à jour chaque minute

    return () => clearInterval(timer);
  }, []);

  // Fonction pour formater la date au format ISO 8601
  const formatDateToISO = (date) => {
    if (!date) return null;
    
    // Créer une nouvelle date avec l'heure à 00:00:00
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    
    // Retourner au format ISO 8601 avec Z à la fin
    return d.toISOString();
  };

  // Fonction pour formater la date de début de journée (00:00:00) en heure locale
  const formatDateToISOStart = (date) => {
    if (!date) return null;
    
    // Créer une nouvelle date en copiant la date originale
    const d = new Date(date);
    
    // Construire manuellement la chaîne ISO avec l'heure locale
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    // Retourner au format ISO 8601 avec T00:00:00.000Z
    return `${year}-${month}-${day}T00:00:00.000Z`;
  };

  // Fonction pour formater la date de fin de journée (23:59:59) en heure locale
  const formatDateToISOEnd = (date) => {
    if (!date) return null;
    
    // Créer une nouvelle date en copiant la date originale
    const d = new Date(date);
    
    // Construire manuellement la chaîne ISO avec l'heure locale
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    // Retourner au format ISO 8601 avec T23:59:59.999Z
    return `${year}-${month}-${day}T23:59:59.999Z`;
  };

  // Formate l'heure au format HH:MM
  const formatHour = (isoString) => {
    if (!isoString) return '--:--';
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return '--:--';
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  // Détermine la couleur de l'heure en fonction de la conformité
  const getShiftTimeColor = (realTime, plannedTime, isStartTime) => {
    const planned = new Date(plannedTime);
    const now = new Date();
    
    if (!realTime) {
      // Si pas de donnée réelle et l'heure est dépassée, afficher en rouge
      if (now > planned) {
        return '#ff0000';
      }
      return 'rgba(255, 255, 255, 0.8)'; // Couleur par défaut si pas dépassé
    }
    
    const real = new Date(realTime);
    
    if (isStartTime) {
      // Pour l'heure de début : vert si réelle <= prévue (arrivé à l'heure ou tôt)
      return real <= planned ? '#00ff00' : '#ff0000';
    } else {
      // Pour l'heure de fin : vert si réelle >= prévue (parti à l'heure ou tard)
      return real >= planned ? '#00ff00' : '#ff0000';
    }
  };

  // Calcule la position (left) et la largeur (width) sur la fenêtre 06h-21h en se basant sur 63vw de largeur disponible
  const getShiftPosition = (startIso, endIso) => {
    if (!startIso || !endIso) return { left: '0vw', width: '0vw' };
    const start = new Date(startIso);
    const end = new Date(endIso);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      return { left: '0vw', width: '0vw' };
    }

    const startHour = 6; // début de la fenêtre affichée
    const totalMinutes = 15 * 60; // 06h -> 21h = 15 heures
    const trackVw = 63; // largeur du scheduler en vw

    const minutesFromStart = (start.getHours() * 60 + start.getMinutes()) - (startHour * 60);
    const minutesToEnd = (end.getHours() * 60 + end.getMinutes()) - (startHour * 60);
    
    const clampedStart = Math.max(0, Math.min(totalMinutes, minutesFromStart));
    const clampedEnd = Math.max(clampedStart, Math.min(totalMinutes, minutesToEnd));

    const leftVw = (clampedStart / totalMinutes) * trackVw;
    const widthVw = ((clampedEnd - clampedStart) / totalMinutes) * trackVw;

    console.log(`Shift de ${startIso} à ${endIso} => left: ${leftVw}vw, width: ${widthVw}vw`);

    return { left: `${leftVw}vw`, width: `${widthVw}vw` };
  };

  // Récupération des users quand l'équipe change
  useEffect(() => {
    const fetchUsers = async () => {
      // Si pas d'équipe sélectionnée, vider la liste
      if (!selectedTeam) {
        setUsers([]);
        setSelectedUserId(null);
        setShiftsByUser({});
        setShiftsError(null);
        setLoadingShifts(false);
        return;
      }

      setLoadingUsers(true);
      setUsersError(null);

      try {
        // console.log('Fetching users for team:', selectedTeam);
        const response = await fetch(`/api/users/teams/${selectedTeam}/`, {
          method: 'GET',
          headers: getAuthHeaders(),
        });

        if (response.ok) {
          const usersData = await response.json();
          
          // Gérer différents formats de réponse
          const usersList = Array.isArray(usersData) ? usersData : 
                           Array.isArray(usersData.users) ? usersData.users : [];
          
          setUsers(usersList);
          
          // Sélectionner automatiquement le premier user si disponible
          if (usersList.length > 0) {
            setSelectedUserId(usersList[0].id);
          } 
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des users:', error);
        setUsersError(error.message);
        setUsers([]); // Vider la liste en cas d'erreur
        setSelectedUserId(null);
      } finally {
        setLoadingUsers(false);
      }
    };

    const fetchShifts = async () => {
      if (!selectedTeam || !selectedDate) {
        setShiftsByUser({});
        return;
      }

      setLoadingShifts(true);
      setShiftsError(null);
      
      try {
        // Convertir la date au format ISO 8601 pour toute la journée
        const fromDate = formatDateToISOStart(selectedDate);  // 00:00:00
        const toDate = formatDateToISOEnd(selectedDate);      // 23:59:59
        
        // console.log('Fetching shifts for team:', selectedTeam, 'from:', fromDate, 'to:', toDate);
        
        const response = await fetch(`/api/teams/${selectedTeam}/calendar?from=${fromDate}&to=${toDate}`, {
          method: 'GET',
          headers: getAuthHeaders(),
        });

        if (response.ok) {
          const shiftsData = await response.json();
          // console.log('Shifts reçus pour l\'équipe:', selectedTeam, 'journée complète:', shiftsData);

          const results = Array.isArray(shiftsData)
            ? shiftsData
            : Array.isArray(shiftsData.results)
              ? shiftsData.results
              : [];

          // Grouper les shifts par user_id
          const grouped = results.reduce((acc, shift) => {
            const userId = shift.user_id || shift.user;
            if (!userId) return acc;
            if (!acc[userId]) acc[userId] = [];
            acc[userId].push(shift);
            return acc;
          }, {});

          setShiftsByUser(grouped);
        } else {
          setShiftsByUser({});
          setShiftsError('Impossible de récupérer les shifts');
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des shifts:', error);
        setShiftsByUser({});
        setShiftsError(error.message);
      } finally {
        setLoadingShifts(false);
      }
    };

    fetchUsers().then(() => {
      fetchShifts();
    });

  }, [selectedTeam, selectedDate]); // Ajouté selectedDate dans les dépendances

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
  const currentTeam = teams?.find(team => team.id === selectedTeam);

  // Fonction pour gérer la sélection d'un user
  const handleUserSelect = (userId) => {
    setSelectedUserId(userId);
    // console.log("User sélectionné:", userId);
  };

  // Fonction pour calculer les styles de positionnement du user card
  const getUserCardStyle = (firstShift, userIndex) => {
    if (!firstShift) {
      return { position: 'relative' };
    }
    const positionStyle = getShiftPosition(firstShift.start_time, firstShift.end_time);
    console.log("Position du user card:", positionStyle, "index:", userIndex);
    return {
      position: 'absolute',
      top: `${userIndex * 60}px`, // Espacement vertical entre les user cards
      left: positionStyle.left,
      width: positionStyle.width,
      minWidth: '80px',
    };
  };

  // console.log("Équipe sélectionnée:", selectedTeam);
  // console.log("Users de l'équipe:", users);
  // console.log("User sélectionné:", selectedUserId);

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

      <div className="users-list">
        {loadingUsers ? (
          <p>Chargement des utilisateurs...</p>
        ) : usersError ? (
          <p className="error">Erreur: {usersError}</p>
        ) : users.length > 0 ? (
          <div className="users-grid">
            {users.map((user, index) => {
              const userShifts = shiftsByUser[user.id] || [];
              // Ne pas afficher si pas de shift
              if (userShifts.length === 0) return null;
              
              // Si l'utilisateur a au moins un shift, on positionne selon le premier
              const firstShift = userShifts[0];
              const positionStyle = firstShift
                ? getShiftPosition(firstShift.start_time, firstShift.end_time)
                : {};

                // console.log("Rendu de l'utilisateur:", user.id, "avec shift:", firstShift); 

                return (
                <div 
                  key={user.id} 
                  className={`user-card ${selectedUserId === user.id ? 'selected' : ''}`}
                  style={getUserCardStyle(firstShift, index)}
                  onClick={() => handleUserSelect(user.id)}
                >
                  <div className={`user-real-shift ${selectedUserId === user.id ? 'selected' : ''}`}>
                  <div className="shift-header">
                    <h3>{`${user.first_name} ${user.last_name[0]}.`}</h3>
                    {loadingShifts ? (
                    <span className="shift-info">...</span>
                    ) : firstShift ? (
                    <span className="shift-info">
                      <span style={{ color: getShiftTimeColor(firstShift.real_start_time, firstShift.start_time, true) }}>
                      {formatHour(firstShift.real_start_time)}
                      </span>
                      {' - '}
                      <span style={{ color: getShiftTimeColor(firstShift.real_end_time, firstShift.end_time, false) }}>
                      {formatHour(firstShift.real_end_time)}
                      </span>
                    </span>
                    ) : null}
                  </div>
                  </div>

                </div>
                );
              })}
              </div>
            ) : (
              <p className="no-users">Aucun membre trouvé pour cette équipe</p>
            )}
            </div>
            </div>
            </div>

            <PersonalInfo selectedUserId={selectedUserId} selectedDate={selectedDate} />

          </>
          );
}
