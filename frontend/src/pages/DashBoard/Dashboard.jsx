import React, { useState } from 'react';
import './Dashboard.css';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const Dashboard = () => {
  const [pointeages, setPointeages] = useState({
    matinIn: null,
    matinOff: null,
    apresMidiIn: null,
    apresMidiOff: null,
  });

  const heuresPrevues = {
    matinIn: '08:00',
    matinOff: '12:00',
    apresMidiIn: '14:00',
    apresMidiOff: '18:00',
  };

  const handleClick = (type) => {
    const now = new Date();
    const formattedTime = now.getHours().toString().padStart(2, '0') + ':' +
                          now.getMinutes().toString().padStart(2, '0');
    setPointeages({
      ...pointeages,
      [type]: formattedTime,
    });
  };

  const getColor = (type) => {
    if (!pointeages[type]) return 'black';

    const [realH, realM] = pointeages[type].split(':').map(Number);
    const [plannedH, plannedM] = heuresPrevues[type].split(':').map(Number);

    if (type.includes('In')) {
      return (realH < plannedH || (realH === plannedH && realM <= plannedM)) ? 'green' : 'red';
    } else {
      return (realH > plannedH || (realH === plannedH && realM >= plannedM)) ? 'green' : 'red';
    }
  };

  // Calcul du pourcentage de présence pour le cercle
  const totalSlots = 4; // matinIn, matinOff, apresMidiIn, apresMidiOff
  const filledSlots = Object.values(pointeages).filter(Boolean).length;
  const percentage = Math.round((filledSlots / totalSlots) * 100);

  return (
    <div style={{ marginLeft: '250px', padding: '20px' }}>
      <h1>Dashboard</h1>

      {/* SECTION CHECK-IN / POINTAGE */}
      <div className="section">
        <h2 className="section-title">Check-In / Pointage</h2>

        {/* Bloc Matin */}
        <div className="bloc">
          <div className="bloc-title">
            <h3>Matin</h3>
          </div>
          <div className="button-row">
            <div>
              <button onClick={() => handleClick('matinIn')}>In</button>
              <span className="time" style={{ color: pointeages.matinIn ? getColor('matinIn') : 'black', marginLeft: '10px' }}>
                {pointeages.matinIn ? `Réel ${pointeages.matinIn}` : `Prévu ${heuresPrevues.matinIn}`}
              </span>
            </div>
            <div>
              <button onClick={() => handleClick('matinOff')}>Off</button>
              <span className="time" style={{ color: pointeages.matinOff ? getColor('matinOff') : 'black', marginLeft: '10px' }}>
                {pointeages.matinOff ? `Réel ${pointeages.matinOff}` : `Prévu ${heuresPrevues.matinOff}`}
              </span>
            </div>
          </div>
        </div>

        {/* Bloc Après-midi */}
        <div className="bloc">
          <div className="bloc-title">
            <h3>Après-midi</h3>
          </div>
          <div className="button-row">
            <div>
              <button onClick={() => handleClick('apresMidiIn')}>In</button>
              <span className="time" style={{ color: pointeages.apresMidiIn ? getColor('apresMidiIn') : 'black', marginLeft: '10px' }}>
                {pointeages.apresMidiIn ? `Réel ${pointeages.apresMidiIn}` : `Prévu ${heuresPrevues.apresMidiIn}`}
              </span>
            </div>
            <div>
              <button onClick={() => handleClick('apresMidiOff')}>Off</button>
              <span className="time" style={{ color: pointeages.apresMidiOff ? getColor('apresMidiOff') : 'black', marginLeft: '10px' }}>
                {pointeages.apresMidiOff ? `Réel ${pointeages.apresMidiOff}` : `Prévu ${heuresPrevues.apresMidiOff}`}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION STATISTIQUES */}
      <div className="section">
        <h2 className="section-title">Statistiques</h2>
        <div style={{ width: '150px', margin: '20px auto' }}>
          <CircularProgressbar
            value={percentage}
            text={`${percentage}%`}
            styles={buildStyles({
              textSize: '18px',
              pathColor: `#007bff`,
              textColor: '#333',
              trailColor: '#eee',
            })}
          />
          <p style={{ textAlign: 'center', marginTop: '10px' }}>Présence</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
