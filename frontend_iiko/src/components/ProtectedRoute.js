// src/components/ProtectedRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import { getCookies } from '../utils/cookies';

const ProtectedRoute = ({ children }) => {
  const accessToken = getCookies('access_token');

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;