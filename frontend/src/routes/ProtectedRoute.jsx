// src/routes/ProtectedRoute.jsx
import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useUser } from "../context/UserContext";
import { hasAnyRole } from "../acl/roles";
import { getRefresh, getRefreshExpiry, isPast } from "../api/auth";
export default function ProtectedRoute({ allow }) {
  const { user, booting } = useUser();
  const location = useLocation();

  // 0️⃣ Attente du bootstrap du UserContext (restauration de session)
  if (booting) {
    return <div style={{ padding: 24 }}>Chargement…</div>;
  }

  // 1️⃣ Vérifie qu’on a un refresh token valide (session existante)
  const hasRefresh = !!getRefresh() && !isPast(getRefreshExpiry());
  if (!hasRefresh) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // 2️⃣ Vérifie les rôles si besoin
  const rawRole = user?.role;
  const roleName =
    typeof rawRole === "string"
      ? rawRole
      : rawRole?.name ?? user?.roleName ?? "";
  const roleLc = (roleName || "").toLowerCase();

  if (Array.isArray(allow) && allow.length > 0) {
    if (!hasAnyRole(roleLc, allow)) {
      return <Navigate to="/403" replace />;
    }
  }

  // 3️⃣ Tout est bon → affiche la page demandée
  return <Outlet />;
}
