// frontend/src/pages/LoginPage.jsx (Mit Redirect für eingeloggte User)

import React, { useState, useContext, useEffect } from 'react'; // useEffect hinzugefügt
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './FormPages.module.css';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    // NEU: Hole auch isAuthenticated direkt aus dem Context
    const { login, isAuthenticated } = useContext(AuthContext);

    // --- NEU: useEffect Hook für Redirect ---
    useEffect(() => {
        // Wenn die Komponente geladen wird UND der User bereits eingeloggt ist...
        if (isAuthenticated) {
            console.log("LoginPage useEffect: User is already authenticated, redirecting to /userdashboard");
            // ...dann sofort zum Dashboard weiterleiten. Verhindert, dass eingeloggte User auf /login bleiben.
            navigate('/userdashboard', { replace: true }); // replace: true ersetzt den Login-Eintrag in der History
        }
        // Abhängigkeit: isAuthenticated. Führe den Effekt aus, wenn sich der Login-Status ändert.
    }, [isAuthenticated, navigate]);
    // --- ENDE NEU ---


    const handleSubmit = async (event) => {
        event.preventDefault();
        setError('');
        console.log('Sende Login-Anfrage für:', username);

        try {
            const apiUrl = 'http://127.0.0.1:8000/api/auth/login/';
            const payload = { username: username, password };

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                const data = await response.json();
                const token = data.key;
                console.log('Login API erfolgreich! Token:', token);
                login(token); // Context updaten -> löst oben useEffect aus, der dann navigiert
                console.log('AuthContext login function called. Navigation should be handled by useEffect.');
                // navigate('/userdashboard'); // Diese Zeile ist jetzt redundant, da useEffect das übernimmt. Könnte man entfernen.
            } else {
                let errorMsg = 'Login fehlgeschlagen. Benutzername/E-Mail oder Passwort falsch.';
                try {
                    const errorData = await response.json();
                    console.error('Login failed (Backend Response):', errorData);
                    errorMsg = errorData.non_field_errors?.[0] || errorData.detail || JSON.stringify(errorData) || errorMsg;
                } catch (e) {
                    console.error('Fehler beim Parsen der Fehlerantwort:', e);
                    errorMsg = `Fehler: ${response.status} ${response.statusText}`;
                }
                setError(errorMsg);
            }
        } catch (error) {
            console.error('Netzwerk- oder anderer Fehler beim Login:', error);
            setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es erneut.');
        }
    };

    // JSX mit CSS-Klassen
    return (
        <div className={styles.formContainer}>
            <h2 className={styles.formTitle}>Login</h2>
            <form onSubmit={handleSubmit}>
                {error && <p className={styles.error}>{error}</p>}
                <div className={styles.formGroup}>
                    <label htmlFor="login-username">Benutzername oder E-Mail:</label>
                    <input type="text" id="login-username" value={username} onChange={(e) => setUsername(e.target.value)} required autoComplete="username" />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="login-password">Passwort:</label>
                    <input type="password" id="login-password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
                </div>
                <button type="submit" className={styles.submitButton}>Einloggen</button>
            </form>
            <p className={styles.switchForm}>
                Noch kein Konto? <Link to="/">Zurück zur Auswahl</Link>
            </p>
        </div>
    );
}

export default LoginPage;