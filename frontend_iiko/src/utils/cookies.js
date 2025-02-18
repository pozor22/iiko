// src/utils/cookies.js
export const setCookies = (name, value, days = 7) => {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value}; ${expires}; path=/`;
  };
  
  export const getCookies = (name) => {
    const cookieName = `${name}=`;
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(cookieName)) {
        return cookie.substring(cookieName.length, cookie.length);
      }
    }
    return null;
  };
  
  export const deleteCookies = (name) => {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  };