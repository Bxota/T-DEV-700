import React, { useState, useEffect } from "react";
import "react-datepicker/dist/react-datepicker.css";
import { getAuthHeaders } from "../../api/auth";
import PersonalInfo from "./PersonalInfo";
import "./css/Planning.css";


export default function Planning({ selectedTeam, selectedDate, teams }) {
  // Changez le nombre ici pour avoir plus de colonnes
  const hours = Array.from({ length: 15 }, (_, i) => 7 + i); // 15 colonnes au lieu de 11
  const [currentTime, setCurrentTime] = useState(new Date());
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [usersError, setUsersError] = useState(null);

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

  // Récupération des users quand l'équipe change
  useEffect(() => {
    const fetchUsers = async () => {
      // Si pas d'équipe sélectionnée, vider la liste
      if (!selectedTeam) {
        setUsers([]);
        setSelectedUserId(null);
        return;
      }

      setLoadingUsers(true);
      setUsersError(null);

      try {
        console.log('Fetching users for team:', selectedTeam);
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
      if (!selectedTeam || !selectedDate) return;
      
      try {
        // Convertir la date au format ISO 8601 pour toute la journée
        const fromDate = formatDateToISOStart(selectedDate);  // 00:00:00
        const toDate = formatDateToISOEnd(selectedDate);      // 23:59:59
        
        console.log('Fetching shifts for team:', selectedTeam, 'from:', fromDate, 'to:', toDate);
        
        const response = await fetch(`/api/teams/${selectedTeam}/calendar?from=${fromDate}&to=${toDate}`, {
          method: 'GET',
          headers: getAuthHeaders(),
        });

        if (response.ok) {
          const shiftsData = await response.json();
          console.log('Shifts reçus pour l\'équipe:', selectedTeam, 'journée complète:', shiftsData);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des shifts:', error);
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
            {users.map(user => (
              <div 
                key={user.id} 
                className={`user-card ${selectedUserId === user.id ? 'selected' : ''}`}
                onClick={() => handleUserSelect(user.id)}
              >
                <div className={`user-real-shift ${selectedUserId === user.id ? 'selected' : ''}`}>
                  <h3>{`${user.first_name} ${user.last_name[0]}.`} </h3>
                  <h3>75% </h3>

                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-users">Aucun membre trouvé pour cette équipe</p>
        )}
      </div>
        </div>
      </div>

      <PersonalInfo selectedUserId={selectedUserId} />

    </>
  );
}
