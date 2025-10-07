import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '../pages/DashBoard/Dashboard';
import Manager from '../pages/Manager/Manager';
import Profile from '../pages/Profile/Profile';
import Team from '../pages/Team/Team';
import Login from '../pages/Login/Login'

const AppRoutes = () => {
  return (
    <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/manager" element={<Manager />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/team" element={<Team />} />
      <Route path="/login" element={<Login />} />
    </Routes>
  );
};

export default AppRoutes;