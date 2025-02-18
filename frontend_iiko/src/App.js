// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { UserProvider } from './context/UserContext'; // Импортируем UserProvider
import Header from './components/Header';
import RegistrationForm from './components/RegistrationForm';
import LoginForm from './components/LoginForm';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';

const App = () => {
  return (
    <UserProvider>
      <Router>
        <Header />
        <Routes>
          <Route path="/register" element={<RegistrationForm />} />
          <Route path="/login" element={<LoginForm />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </UserProvider>
  );
};

export default App;