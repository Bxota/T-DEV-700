import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';
import { useUser } from '../../context/UserContext';
import { ROLE, hasAnyRole } from '../../acl/roles';

const Sidebar = () => {
  const location = useLocation();
  const { user, isLoggedIn } = useUser();

  // ❌ Cache complètement la sidebar quand non connecté ou sur la page login
  if (!isLoggedIn || location.pathname.startsWith('/login')) {
    return null;
  }

  // Rôle tolérant (objet ou string)
  const rawRole = user?.role;
  const roleName = (typeof rawRole === 'string' ? rawRole : rawRole?.name) ?? user?.roleName ?? '';
  const roleLc = roleName.toLowerCase();

  const menuItems = [
    { path: '/dashboard', name: 'Tableau de bord', icon: '📊', allow: [ROLE.MANAGER, ROLE.EMPLOYEE] },
    { path: '/manager',   name: 'Gestionnaire',    icon: '👔', allow: [ROLE.MANAGER] },
    { path: '/horaires',  name: 'Horaires', icon: '🗓️', allow: [ROLE.MANAGER, ROLE.EMPLOYEE] },
    { path: '/team',      name: 'Équipe',          icon: '👥', allow: [ROLE.MANAGER, ROLE.EMPLOYEE] },
    { path: '/users',     name: 'Utilisateurs',    icon: '🧑‍💼', allow: [ROLE.MANAGER] },
    { path: '/profile',   name: 'Profil',          icon: '👤', allow: [ROLE.MANAGER, ROLE.EMPLOYEE] },
  ];

  const visibleItems = menuItems.filter(item => hasAnyRole(roleLc, item.allow));

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Menu</h2>
      </div>
      <nav className="sidebar-nav">
        <ul>
          {visibleItems.map((item) => (
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
