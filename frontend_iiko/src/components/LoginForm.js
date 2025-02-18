// src/components/LoginForm.js
import React, { useState, useContext } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { setCookies } from '../utils/cookies';
import { UserContext } from '../context/UserContext'; // Импортируем контекст

const LoginForm = () => {
  const [isCodeLogin, setIsCodeLogin] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    code: '',
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setUser } = useContext(UserContext); // Используем контекст

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      let response;
      if (isCodeLogin) {
        response = await axios.post('http://127.0.0.1:8000/api/users/login_code/', {
          code: formData.code,
        });
      } else {
        response = await axios.post('http://127.0.0.1:8000/api/users/login/', {
          username: formData.username,
          password: formData.password,
        });
      }

      const { access, refresh, user } = response.data;

      // Сохраняем токены в cookies
      setCookies('access_token', access);
      setCookies('refresh_token', refresh);

      // Сохраняем данные пользователя в контекст
      setUser(user);

      // Перенаправляем пользователя на защищенную страницу
      navigate('/dashboard');
    } catch (err) {
      setError(isCodeLogin ? 'Неверный код' : 'Неверное имя пользователя или пароль');
      console.error(err);
    }
  };

  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2>Авторизация</h2>
        {error && <p style={styles.error}>{error}</p>}

        <button
          type="button"
          onClick={() => setIsCodeLogin(!isCodeLogin)}
          style={styles.toggleButton}
        >
          {isCodeLogin ? 'Авторизация по логину и паролю' : 'Авторизация по коду'}
        </button>

        {isCodeLogin ? (
          <div style={styles.formGroup}>
            <label>Код:</label>
            <input
              type="number"
              name="code"
              value={formData.code}
              onChange={handleChange}
              placeholder="Введите 6-значный код"
              required
            />
          </div>
        ) : (
          <>
            <div style={styles.formGroup}>
              <label>Имя пользователя:</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <label>Пароль:</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
          </>
        )}

        <button type="submit" style={styles.submitButton}>
          {isCodeLogin ? 'Войти по коду' : 'Войти'}
        </button>
      </form>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#fff',
  },
  form: {
    backgroundColor: '#f0f0f0',
    padding: '20px',
    borderRadius: '10px',
    boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
    width: '300px',
  },
  formGroup: {
    marginBottom: '15px',
  },
  submitButton: {
    backgroundColor: '#800080',
    color: '#fff',
    padding: '10px 15px',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    width: '100%',
  },
  toggleButton: {
    backgroundColor: '#4B0082',
    color: '#fff',
    padding: '10px 15px',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    width: '100%',
    marginBottom: '15px',
  },
  error: {
    color: 'red',
    fontSize: '14px',
  },
};

export default LoginForm;