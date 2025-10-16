export const ROLE = {
  MANAGER: 'manager',
  EMPLOYEE: 'employee',
};

// Pages / sections visibles
export const ACL = {
  dashboard: [ROLE.MANAGER, ROLE.EMPLOYEE],
  profile:   [ROLE.MANAGER, ROLE.EMPLOYEE],
  teams:     [ROLE.MANAGER, ROLE.EMPLOYEE], // 👈 employee peut voir
  users:     [ROLE.MANAGER],
  manager:   [ROLE.MANAGER],
};

// Capacités (permissions fonctionnelles)
export const PERM = {
  manageTeams: [ROLE.MANAGER],                  // créer / éditer / supprimer
  viewTeams:   [ROLE.MANAGER, ROLE.EMPLOYEE],   // lecture seule
};

export const hasAnyRole = (roleName, allowed = []) =>
  !!roleName && allowed.map(r => String(r).toLowerCase()).includes(String(roleName).toLowerCase());

export const can = (roleName, permKey) => {
  const allowed = PERM[permKey] || [];
  return hasAnyRole(roleName, allowed);
};
