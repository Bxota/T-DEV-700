import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ImgLogin.css';
import profileIcon from '../../assets/imgProfil.png';
import { useUser } from '../../context/UserContext';

const getInitials = (first, last, name, email) => {
  if (first || last) {
    const a = (first?.[0] || '').toUpperCase();
    const b = (last?.[0]  || '').toUpperCase();
    const two = (a + b).trim();
    if (two) return two;
  }
  if (name) {
    return name
      .split(' ')
      .filter(Boolean)
      .map(n => n[0]?.toUpperCase() || '')
      .join('')
      .slice(0, 2) || '?';
  }
  if (email) return (email.split('@')[0]?.slice(0, 2) || '?').toUpperCase();
  return '?';
};

const ImgLogin = () => {
  const { user, isLoggedIn } = useUser();
  const navigate = useNavigate();
  const [avatarOk, setAvatarOk] = useState(false);

  const initials = useMemo(
    () => getInitials(user?.first_name, user?.last_name, user?.name, user?.email),
    [user?.first_name, user?.last_name, user?.name, user?.email]
  );

  useEffect(() => {
    if (!user?.avatarUrl) { setAvatarOk(false); return; }
    const img = new Image();
    img.onload = () => setAvatarOk(true);
    img.onerror = () => setAvatarOk(false);
    img.src = user.avatarUrl;
  }, [user?.avatarUrl]);

  const goToLogin = () => navigate('/login');
  const goToProfileOrLogin = () => navigate(isLoggedIn ? '/profile' : '/login');

  // 🟣 Cas "déconnecté" OU "initiales inconnues (?)" → on montre le logo invité qui renvoie vers /login
  const showAsGuest = !isLoggedIn || initials === '?';
  if (showAsGuest) {
    return (
      <div
        className="image-button"
        onClick={goToLogin}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && goToLogin()}
        title="Se connecter"
      >
        <img src={profileIcon} alt="Se connecter" />
      </div>
    );
  }

  // 🖼️ Avatar personnalisé
  if (user?.avatarUrl && avatarOk) {
    return (
      <div
        className="image-button avatar"
        style={{ backgroundImage: `url(${user.avatarUrl})` }}
        onClick={goToProfileOrLogin}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && goToProfileOrLogin()}
        title="Mon profil"
      />
    );
  }

  // 🔤 Initiales (même look que le profil)
  return (
    <div
      className="image-button initials"
      onClick={goToProfileOrLogin}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && goToProfileOrLogin()}
      title="Mon profil"
    >
      {initials}
    </div>
  );
};

export default ImgLogin;
