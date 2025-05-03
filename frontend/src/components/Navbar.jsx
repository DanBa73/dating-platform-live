// frontend/src/components/Navbar.jsx (mit Favoriten-Link und Benachrichtigungscenter)

import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import NotificationCenter from './NotificationCenter.jsx';

function Navbar() {
  const { isAuthenticated, logout, user } = useContext(AuthContext);
  const isModerator = user?.is_staff === true;
  const navigate = useNavigate();

  // Logout-Handler ruft jetzt logout() vom Context auf und leitet weiter
  const handleLogout = () => {
    logout(); // <-- Ruft Context-Funktion auf (löscht Token aus State/localStorage)
    navigate('/login'); // <-- Leitet zur Login-Seite weiter
  };

  // Styles (unverändert)
  const navStyle = {
    padding: '1rem',
    backgroundColor: '#f0f0f0',
    marginBottom: '1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };
  const linkStyle = {
    marginRight: '1rem',
    textDecoration: 'none',
    color: '#333'
  };
  const buttonStyle = {
    padding: '0.3rem 0.6rem',
    cursor: 'pointer'
  };


  return (
    <nav style={navStyle}>
      <div>
            <Link to="/" style={linkStyle}>Dating Platform</Link>
            {/* Links für eingeloggte Benutzer basierend auf Rolle */}
            {isAuthenticated && !isModerator && (
              <>
                <Link to="/userdashboard" style={linkStyle}>Dashboard</Link>
                <Link to="/conversations" style={linkStyle}>Meine Gespräche</Link>
                <Link to="/favorites" style={linkStyle}>Meine Favoriten</Link>
              </>
            )}
            {/* Nur für Moderatoren */}
            {isAuthenticated && isModerator && (
              <>
                <Link to="/moderator/dashboard" style={linkStyle}>Dashboard</Link>
              </>
            )}
      </div>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {/* Benachrichtigungscenter nur für normale Benutzer */}
        {isAuthenticated && !isModerator && <NotificationCenter />}
        
        {/* Bedingte Anzeige basierend auf isAuthenticated */}
        {isAuthenticated ? (
          // Wenn eingeloggt: Zeige Logout Button
          <button onClick={handleLogout} style={buttonStyle}>Logout</button>
        ) : (
          // Wenn nicht eingeloggt: Zeige Login und Register Links
          <>
            <Link to="/login" style={linkStyle}>Login</Link>
            <Link to="/register" style={{...linkStyle, marginRight: 0}}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
// Ende der Datei Navbar.jsx (mit Favoriten-Link)
