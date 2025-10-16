// src/routes/ProtectedRoute.jsx
import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { hasAnyRole } from '../acl/roles';

export default function ProtectedRoute({ allow }) {
  const { user } = useUser();
  const location = useLocation();

  // 1) Non connecté -> login
  const isLoggedIn = !!user?.id || !!user?.email;
  if (!isLoggedIn) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const rawRole = user?.role;
  const roleName =
    typeof rawRole === 'string'
      ? rawRole
      : rawRole?.name ?? user?.roleName ?? '';
  const roleLc = roleName.toLowerCase();

  if (Array.isArray(allow) && allow.length > 0) {
    if (!hasAnyRole(roleLc, allow)) {
      return <Navigate to="/403" replace />;
    }
  }

  // 3) OK
  return <Outlet />;
}
