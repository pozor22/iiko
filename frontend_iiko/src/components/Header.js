// src/components/Header.js
import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCookies, deleteCookies } from '../utils/cookies'; // Импортируем getCookies и deleteCookies
import { UserContext } from '../context/UserContext';

const Header = () => {
  const navigate = useNavigate();
  const { user, setUser } = useContext(UserContext);
  const accessToken = getCookies('access_token'); // Теперь getCookies определена

  const handleLogout = () => {
    deleteCookies('access_token');
    deleteCookies('refresh_token');
    setUser(null); // Сбрасываем данные пользователя
    navigate('/login');
  };

  return (
    <header style={styles.header}>
      <div style={styles.logo}>vovaiiko</div>
      <div>
        {accessToken ? (
          <>
            <span style={styles.userName}>{user?.username}</span> {/* Отображаем имя пользователя */}
            <button onClick={handleLogout} style={styles.button}>
              Выйти
            </button>
          </>
        ) : (
          <>
            <Link to="/register" style={styles.button}>Регистрация</Link>
            <Link to="/login" style={styles.button}>Авторизация</Link>
          </>
        )}
      </div>
    </header>
  );
};

const styles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#000',
    padding: '10px 20px',
  },
  logo: {
    color: '#fff',
    fontSize: '24px',
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: '#800080',
    color: '#fff',
    padding: '10px 15px',
    marginLeft: '10px',
    borderRadius: '5px',
    textDecoration: 'none',
    fontSize: '16px',
    cursor: 'pointer',
    border: 'none',
  },
  userName: {
    color: '#fff',
    marginRight: '10px',
  },
};

export default Header;