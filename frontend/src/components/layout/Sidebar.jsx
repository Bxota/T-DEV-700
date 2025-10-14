import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    {
      path: '/dashboard',
      name: 'Tableau de bord',
      icon: '📊'
    },
    {
      path: '/team',
      name: 'Équipe',
      icon: '👥'
    },
        {
      path: '/users',
      name: 'Utilisateurs',
      icon: '🧑‍💼'
    },
    {
      path: '/manager',
      name: 'Gestionnaire',
      icon: '👔'
    },
    {
      path: '/profile',
      name: 'Profil',
      icon: '👤'
    }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Menu</h2>
      </div>
      <nav className="sidebar-nav">
        <ul>
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-text">{item.name}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;