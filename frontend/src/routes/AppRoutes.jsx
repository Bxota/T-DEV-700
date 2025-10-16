// src/routes/AppRoutes.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '../pages/DashBoard/Dashboard';
import Manager from '../pages/Manager/Manager';
import Profile from '../pages/Profile/Profile';
import Team from '../pages/Team/Team';
import Login from '../pages/Login/Login'
import Users from '../pages/Users/Users';
import Horaires from '../pages/Horaires/Horaires';

import ProtectedRoute from './ProtectedRoute';
import { ROLE } from '../acl/roles';

const Forbidden = () => (
  <div style={{ padding: 24 }}>
    <h1>403</h1>
    <p>Accès refusé.</p>
  </div>
);

const NotFound = () => (
  <div style={{ padding: 24 }}>
    <h1>404</h1>
    <p>Page introuvable.</p>
  </div>
);

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />

      {/* Redirection racine */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* 👇 Accès commun: employee + manager */}
      <Route element={<ProtectedRoute allow={[ROLE.MANAGER, ROLE.EMPLOYEE]} />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile"   element={<Profile />} />
        <Route path="/team"      element={<Team />} />      {/* <= ICI maintenant */}
      </Route>

      {/* 👇 Accès manager uniquement */}
      <Route element={<ProtectedRoute allow={[ROLE.MANAGER]} />}>
        <Route path="/manager" element={<Manager />} />
        <Route path="/users"   element={<Users />} />
        <Route path="/horaires" element={<Horaires />} />
      </Route>

      <Route path="/403" element={<Forbidden />} />
      <Route path="*"    element={<NotFound />} />
    </Routes>
  );
}
