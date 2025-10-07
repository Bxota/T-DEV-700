import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ImgLogin.css';
import profileIcon from '../../assets/imgProfil.png'; // ton image

const ImageButton = () => {
  const navigate = useNavigate();

  const goToLogin = () => {
    navigate('/login'); 
  };

  return (
    <div className="image-button" onClick={goToLogin}>
      <img src={profileIcon} alt="Se connecter" />
    </div>
  );
};

export default ImageButton;
