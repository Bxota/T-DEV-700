import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ImgLogin.css';
import profileIcon from '../../assets/imgProfil.png';
import { useUser } from '../../context/UserContext';

const getInitials = (name, email) => {
  if (name) {
    return name
      .split(' ')
      .filter(Boolean)
      .map((n) => n[0]?.toUpperCase() || '')
      .join('')
      .slice(0, 2);
  }
  if (email) return (email.split('@')[0]?.[0] || '?').toUpperCase();
  return '?';
};

const ImgLogin = () => {
  const { user, isLoggedIn } = useUser();
  const navigate = useNavigate();
  const [avatarOk, setAvatarOk] = useState(false);
  const initials = useMemo(() => getInitials(user?.name, user?.email), [user]);

  useEffect(() => {
    if (!user?.avatarUrl) {
      setAvatarOk(false);
      return;
    }
    const img = new Image();
    img.onload = () => setAvatarOk(true);
    img.onerror = () => setAvatarOk(false);
    img.src = user.avatarUrl;
  }, [user?.avatarUrl]);

  const goTo = () => navigate(isLoggedIn ? '/profile' : '/login');

  if (!isLoggedIn) {
    return (
      <div
        className="image-button"
        onClick={goTo}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && goTo()}
      >
        <img src={profileIcon} alt="Se connecter" />
      </div>
    );
  }

  if (user.avatarUrl && avatarOk) {
    return (
      <div
        className="image-button avatar"
        style={{ backgroundImage: `url(${user.avatarUrl})` }}
        onClick={goTo}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && goTo()}
      />
    );
  }

  return (
    <div
      className="image-button initials"
      onClick={goTo}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && goTo()}
    >
      {initials}
    </div>
  );
};

export default ImgLogin;
