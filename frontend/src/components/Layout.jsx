// frontend/src/components/Layout.jsx (Angepasst an neue CSS-Struktur)
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { FiLogOut } from 'react-icons/fi';
import styles from './Layout.module.css'; // Zugehöriges CSS-Modul
import { AuthContext } from '../context/AuthContext.jsx';
import NotificationCenter from './NotificationCenter.jsx';
import UnreadIndicator from './UnreadIndicator.jsx';

// Akzeptiert 'solidBackground' und 'moderatorBackground' Props
function Layout({ children, solidBackground, moderatorBackground }) {
  const { isAuthenticated, user, logout } = useContext(AuthContext);

  // Bestimme die korrekte Hintergrundklasse basierend auf den Props
  let backgroundClass = styles.backgroundImage; // Standard: Bild-Hintergrund
  
  if (solidBackground) {
    backgroundClass = styles.solidBackground; // Orchid-Hintergrund für Benutzer-Seiten
  } else if (moderatorBackground) {
    backgroundClass = styles.moderatorBackground; // Grauer Hintergrund für Moderator-Seiten
  }

  return (
    // Wende IMMER die Basisklasse UND die ausgewählte Hintergrundklasse an
    <div className={`${styles.layoutContainer} ${backgroundClass}`}>
      <header className={styles.layoutHeader}>
        <div>
          <Link to="/" className={styles.headerLink}>Dating Platform</Link>
          {isAuthenticated && !moderatorBackground && (
            <>
              <Link to="/userdashboard" className={styles.headerLink}>Dashboard</Link>
              <Link to="/conversations" className={styles.headerLink}>
                Meine Gespräche
                <UnreadIndicator />
              </Link>
              <Link to="/favorites" className={styles.headerLink}>Meine Favoriten</Link>
            </>
          )}
          {isAuthenticated && moderatorBackground && (
            <>
              <Link to="/moderator/dashboard" className={styles.headerLink}>Dashboard</Link>
            </>
          )}
        </div>
        <div className={styles.headerLinks}>
          {isAuthenticated && user ? (
            <>
              <span style={{ marginRight: '15px', display: 'inline-flex', alignItems: 'center' }}>
                Hallo, {user.username}!
              </span>
              {/* Benachrichtigungscenter nur für normale Benutzer */}
              {!moderatorBackground && <NotificationCenter />}
              <button
                onClick={logout}
                className={styles.logoutButton}
                aria-label="Logout"
                title="Logout"
              >
                <FiLogOut size={22} />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className={styles.headerLink}>Login</Link>
              <Link to="/register" className={styles.headerLink}>Register</Link>
            </>
          )}
        </div>
      </header>

      {/* Hauptinhalt bleibt unverändert */}
      <main className={styles.layoutMain}>
        {children}
      </main>
    </div>
  );
}

export default Layout;
