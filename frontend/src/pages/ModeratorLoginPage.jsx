// frontend/src/pages/ModeratorLoginPage.jsx

import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './ModeratorLoginPage.module.css';

function ModeratorLoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  // AuthContext holen, um Login-Funktion und Status zu nutzen
  const { login, isAuthenticated, user, isAuthLoading, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  // --- NEU: useEffect Hook für die Weiterleitung NACH dem Login ---
  useEffect(() => {
    // Nicht weiterleiten, während der Context noch lädt
    if (isAuthLoading) {
      return;
    }

    // Prüfen, ob Login erfolgreich war UND User-Daten geladen sind
    if (isAuthenticated && user) {
      if (user.is_staff) {
        // Erfolgreich als Staff eingeloggt -> zum Moderator-Dashboard
        console.log("ModeratorLoginPage: Staff user detected, redirecting to /moderator/dashboard...");
        navigate('/moderator/dashboard'); // Ziel für Moderatoren (müssen wir noch erstellen)
      } else {
        // Ein normaler User hat sich hier eingeloggt -> Fehler/Ausloggen/Umleiten
        console.log("ModeratorLoginPage: Non-staff user logged in, logging out...");
        logout(); // Loggt den normalen User wieder aus
        setError("Zugriff verweigert. Nur für Moderatoren/Admins.");
        // Optional: navigate('/'); // Oder zur normalen Startseite leiten
      }
    }
    // Abhängigkeiten: Reagiere auf Änderungen im Login-Status oder User-Objekt
  }, [isAuthenticated, user, isAuthLoading, navigate, logout, setError]);


  // Submit-Handler
  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    console.log('Sende Moderator-Login-Anfrage für:', username);

    try {
      const apiUrl = 'http://127.0.0.1:8000/api/auth/login/'; // Gleiche API wie normaler Login
      const payload = { username, password };

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.key;
        console.log('Moderator Login API successful! Token:', token);
        // Rufe login() vom Context auf. Dies speichert den Token
        // UND löst fetchUserDetails aus. Der useEffect oben kümmert
        // sich dann um die Weiterleitung basierend auf user.is_staff.
        login(token);
      } else {
        // Fehlerbehandlung
        let errorMsg = 'Login fehlgeschlagen. Bitte überprüfe deine Eingaben.';
        try {
          const errorData = await response.json();
          console.error('Moderator Login failed (Backend Response):', errorData);
          errorMsg = errorData.non_field_errors?.[0] || errorData.detail || errorMsg;
        } catch (e) {
          console.error('Fehler beim Parsen der Fehlerantwort:', e);
          errorMsg = `Fehler: ${response.status} ${response.statusText}`;
        }
        setError(errorMsg);
      }
    } catch (error) {
      console.error('Netzwerk- oder anderer Fehler beim Login:', error);
      setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es erneut.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // JSX für das Formular mit verbesserten Styles
  return (
    <div className={styles.loginContainer}>
      <h2 className={styles.loginTitle}>Moderator / Admin Login</h2>
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label htmlFor="mod-login-username" className={styles.formLabel}>Benutzername:</label>
          <input 
            type="text" 
            id="mod-login-username" 
            className={styles.formInput}
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            required 
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="mod-login-password" className={styles.formLabel}>Passwort:</label>
          <input 
            type="password" 
            id="mod-login-password" 
            className={styles.formInput}
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
          />
        </div>
        {error && <p className={styles.errorMessage}>{error}</p>}
        <button 
          type="submit" 
          className={styles.submitButton}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Anmeldung...' : 'Anmelden'}
        </button>
      </form>
      <p className={styles.infoText}>
        Nur für Moderatoren und Administratoren. Normale Benutzer verwenden bitte die reguläre Anmeldung.
      </p>
      <Link to="/" className={styles.backLink}>Zurück zur Hauptseite</Link>
    </div>
  );
}

export default ModeratorLoginPage;
// Ende der Datei ModeratorLoginPage.jsx
