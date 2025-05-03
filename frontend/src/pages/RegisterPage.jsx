// frontend/src/pages/RegisterPage.jsx
import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import styles from './FormPages.module.css'; // CSS-Modul importieren

function RegisterPage() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [gender, setGender] = useState('');
    const [seeking, setSeeking] = useState('');
    const [error, setError] = useState(null);

    const { registerUser } = useContext(AuthContext);
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    useEffect(() => {
        const urlGender = searchParams.get('gender');
        const urlSeeking = searchParams.get('seeking');
        if (urlGender) { setGender(urlGender); }
        if (urlSeeking) { setSeeking(urlSeeking); }
    }, [searchParams]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (password !== password2) {
            setError('Passwörter stimmen nicht überein.');
            return;
        }

        const registrationData = {
            username,
            email,
            password1: password,
            password2,
            gender: gender || null,
            seeking: seeking || null,
        };

        console.log("Sende FINALE KORRIGIERTE Registrierungsdaten:", registrationData);

        try {
            const success = await registerUser(registrationData);
            if (success) {
                console.log('Registrierung erfolgreich (Custom, final). Weiterleitung zum Login...');
                navigate('/login', { state: { message: 'Registrierung erfolgreich! Du kannst dich jetzt einloggen.' } });
            } else {
                 setError('Registrierung fehlgeschlagen. Bitte versuche es erneut.');
            }
        } catch (err) {
            console.error("Registrierungsfehler:", err);
            const errorMessage = err.response?.data ? JSON.stringify(err.response.data) : err.message;
            setError(`Registrierung fehlgeschlagen: ${errorMessage}`);
        }
    };

    // JSX mit CSS-Klassen aus FormPages.module.css
    return (
        <div className={styles.formContainer}>
            <h2 className={styles.formTitle}>Nur noch ein Schritt</h2>
            <form onSubmit={handleSubmit}>
                {error && <p className={styles.error}>{error}</p>}

                {/* --- NEU: InfoText-Zeilen entfernt --- */}
                {/* {gender && <p className={styles.infoText}>Dein Geschlecht (auswahl): {gender}</p>} */}
                {/* {seeking && <p className={styles.infoText}>Du suchst (auswahl): {seeking}</p>} */}
                {/* --- ENDE NEU --- */}

                <div className={styles.formGroup}>
                    <label htmlFor="username">Benutzername:</label>
                    <input type="text" id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="email">E-Mail:</label>
                    <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="password">Passwort:</label>
                    <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="password2">Passwort bestätigen:</label>
                    <input type="password" id="password2" value={password2} onChange={(e) => setPassword2(e.target.value)} required />
                </div>

                <button type="submit" className={styles.submitButton}>Konto erstellen</button>
            </form>
            <p className={styles.switchForm}>
                Schon registriert? <Link to="/login">Zum Login</Link>
            </p>
        </div>
    );
}

export default RegisterPage;