import React, { useEffect, useState } from "react";
import { getAuthHeaders } from "../../api/auth";
import "./css/PersonalInfo.css";

const defaultManager = {
  firstName: "Jean",
  lastName: "Dupont",
  position: "Chef d'équipe",
};

export default function PersonalInfo({ selectedUserId }) {
  const [manager, setManager] = useState(defaultManager);
  const [loadingUser, setLoadingUser] = useState(false);
  const [userError, setUserError] = useState(null);
  const [shifts, setShifts] = useState([]);
  const [loadingShifts, setLoadingShifts] = useState(false);
  const [shiftsError, setShiftsError] = useState(null);
  const [reports, setReports] = useState(null);
  const [loadingReports, setLoadingReports] = useState(false);
  const [reportsError, setReportsError] = useState(null);

  useEffect(() => {
    if (!selectedUserId) {
      setManager(defaultManager);
      setUserError(null);
      return;
    }

    let isMounted = true;
    setLoadingUser(true);
    setUserError(null);

    const fetchUser = async () => {
      try {
        const response = await fetch(`/api/users/${selectedUserId}`, {
          headers: getAuthHeaders(),
        });

        if (!response.ok) {
          throw new Error(`Impossible de récupérer l'utilisateur (${response.status})`);
        }

        const data = await response.json();
        if (!isMounted) return;

        const user = data.user || data;
        console.debug("Données utilisateur récupérées", user);

        setManager({
          firstName: user.first_name || user.firstName || defaultManager.firstName,
          lastName: user.last_name || user.lastName || defaultManager.lastName,
          position: (user.role && user.role.name) || user.role_name || user.position || defaultManager.position,
          team: user.team?.name || user.team_name || "",
          email: user.email,
        });
      } catch (error) {
        if (!isMounted) return;
        setUserError(error.message);
        setManager(defaultManager);
      } finally {
        if (isMounted) {
          setLoadingUser(false);
        }
      }
    };

    fetchUser();

    return () => {
      isMounted = false;
    };
  }, [selectedUserId]);

  // Récupération des shifts de l'utilisateur pour aujourd'hui
  useEffect(() => {
    if (!selectedUserId) {
      setShifts([]);
      setShiftsError(null);
      return;
    }

    let isMounted = true;
    setLoadingShifts(true);
    setShiftsError(null);

    const fetchShifts = async () => {
      try {
        // Construire la date d'aujourd'hui en ISO
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const fromDate = today.toISOString();
        today.setHours(23, 59, 59, 999);
        const toDate = today.toISOString();

        const url = `/api/users/${selectedUserId}/shifts/list?from=${encodeURIComponent(fromDate)}&to=${encodeURIComponent(toDate)}`;
        const response = await fetch(url, {
          headers: getAuthHeaders(),
        });

        if (!response.ok) {
          throw new Error(`Impossible de récupérer les shifts (${response.status})`);
        }

        const data = await response.json();
        if (!isMounted) return;

        const todayShifts = Array.isArray(data) ? data : 
                           Array.isArray(data.results) ? data.results : 
                           Array.isArray(data.shifts) ? data.shifts : [];

        console.debug("Shifts d'aujourd'hui", todayShifts);
        setShifts(todayShifts);
      } catch (error) {
        if (!isMounted) return;
        setShiftsError(error.message);
        setShifts([]);
      } finally {
        if (isMounted) {
          setLoadingShifts(false);
        }
      }
    };

    fetchShifts();

    return () => {
      isMounted = false;
    };
  }, [selectedUserId]);

  // Récupération des reports de l'utilisateur
  useEffect(() => {
    if (!selectedUserId) {
      setReports(null);
      setReportsError(null);
      return;
    }

    let isMounted = true;
    setLoadingReports(true);
    setReportsError(null);

    const fetchReports = async () => {
      try {
        const response = await fetch(`/api/users/${selectedUserId}/reports`, {
          headers: getAuthHeaders(),
        });

        if (!response.ok) {
          throw new Error(`Impossible de récupérer les rapports (${response.status})`);
        }

        const data = await response.json();
        if (!isMounted) return;

        const reportData = data.reports || data;
        console.debug("Rapports utilisateur", reportData);
        setReports(reportData);
      } catch (error) {
        if (!isMounted) return;
        setReportsError(error.message);
        setReports(null);
      } finally {
        if (isMounted) {
          setLoadingReports(false);
        }
      }
    };

    fetchReports();

    return () => {
      isMounted = false;
    };
  }, [selectedUserId]);
  const formatHour = (isoString) => {
    if (!isoString) return '--:--';
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return '--:--';
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  // Horaires de la journée sélectionnée
  const firstShift = shifts.length > 0 ? shifts[0] : null;
  const todaySchedule = {
    date: new Date().toLocaleDateString('fr-FR', { 
      weekday: 'long', 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric' 
    }),
    workStart: firstShift ? formatHour(firstShift.start_time) : "08:00",
    workEnd: firstShift ? formatHour(firstShift.end_time) : "18:00",
  };

  // Statistiques personnelles
  const personalStats = {
    absencesCount: reports?.absences_count || 0,
    absencesRate: reports?.absences_rate || 0,
    latenessCount: reports?.lateness_count || 0,
    latenessRate: reports?.lateness_rate || 0,
    totalShifts: reports?.total_shifts || 0,
    hoursWorked: reports ? (reports.total_worked_minutes / 60).toFixed(1) : 0,
  };

  const absencePercentage = Math.round(personalStats.absencesRate || 0);
  const latenessPercentage = Math.round(personalStats.latenessRate || 0);

  return (
    <div className="personal-info-sidebar">
      {/* Section 1: Nom et Prénom */}
      <div className="personal-identity">
        <div className="identity-info">
          <h2 className="full-name">
            {manager?.firstName || defaultManager.firstName} {manager?.lastName || defaultManager.lastName}
          </h2>
          <p className="position">{manager?.position || defaultManager.position}</p>
        </div>
      </div>

      {/* Section 2: Horaires de la journée */}
      <div className="daily-schedule">
        <div className="schedule-date">{todaySchedule.date}</div>
        <h3 className="section-title">Horaires</h3>
        
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
          {loadingShifts ? (
            <p style={{ fontSize: '0.9em', color: '#999' }}>Chargement...</p>
          ) : shiftsError ? (
            <p style={{ fontSize: '0.9em', color: '#ff6b6b' }}>Erreur: {shiftsError}</p>
          ) : shifts.length > 0 ? (
            shifts.map((shift, index) => (
              <div key={index} className="schedule-item break">
                <span className="event-time">
                  {formatHour(shift.real_start_time)} - {formatHour(shift.real_end_time)}
                </span>
                <span className="event-title">Horaires réel</span>
              </div>
            ))
          ) : (
            <p style={{ fontSize: '0.9em', color: '#999' }}>Aucun shift aujourd'hui</p>
          )}
        </div>
      </div>

      {/* Section 3: Statistiques personnelles */}
      <div className="personal-stats">
        <h3 className="section-title">Statistiques</h3>
        
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-number">{personalStats.totalShifts}</div>
            <div className="stat-label">Shifts totaux</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{personalStats.hoursWorked}h</div>
            <div className="stat-label">Heures travaillées</div>
          </div>
        </div>

        <div className="progress-section">
          <div className="progress-item">
            <div className="progress-header">
              <span className="progress-label">Taux d'absence</span>
              <span className="progress-percentage">{absencePercentage}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${absencePercentage}%` }}
              ></div>
            </div>
          </div>

          <div className="progress-item">
            <div className="progress-header">
              <span className="progress-label">Taux de retard</span>
              <span className="progress-percentage">{latenessPercentage}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill efficiency"
                style={{ width: `${latenessPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* <div className="weekly-summary">
          <h4 className="summary-title">Résumé hebdomadaire</h4>
          <div className="summary-stat">
            <span>Objectif: {personalStats.weeklyGoal}h</span>
            <span>Réalisé: {personalStats.hoursWorked * 5}h</span>
          </div>
        </div> */}
      </div>
    </div>
  );
}
