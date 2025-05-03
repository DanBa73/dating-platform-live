// frontend/src/pages/ReceivedLikesPage.jsx
import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './UserDashboardPage.module.css'; // Wir verwenden die gleichen Styles wie das Dashboard

function ReceivedLikesPage() {
    const { authToken } = useContext(AuthContext);
    const [receivedLikes, setReceivedLikes] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Laden der erhaltenen Likes
    useEffect(() => {
        const fetchReceivedLikes = async () => {
            if (!authToken) return;

            setIsLoading(true);
            setError(null);

            try {
                const response = await fetch('http://127.0.0.1:8000/api/accounts/received-likes/', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${authToken}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    // Überprüfen, ob die Daten paginiert sind
                    if (data.results && Array.isArray(data.results)) {
                        // Wenn ja, verwenden wir data.results als Array
                        setReceivedLikes(data.results);
                    } else if (Array.isArray(data)) {
                        // Wenn die Daten bereits ein Array sind
                        setReceivedLikes(data);
                    } else {
                        // Wenn die Daten weder paginiert noch ein Array sind
                        console.error("Unerwartetes Datenformat:", data);
                        setError("Unerwartetes Datenformat vom Server erhalten.");
                        setReceivedLikes([]);
                    }
                } else {
                    let errorMsg = `Fehler ${response.status}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.detail || JSON.stringify(errorData);
                    } catch (e) {
                        // Ignorieren, wenn keine JSON-Antwort
                    }
                    setError(`Erhaltene Likes konnten nicht geladen werden: ${errorMsg}`);
                }
            } catch (err) {
                setError("Netzwerkfehler beim Laden der erhaltenen Likes.");
                console.error("Fehler beim Laden der erhaltenen Likes:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchReceivedLikes();
    }, [authToken]);

    // Render-Funktionen
    if (isLoading) {
        return <div className={styles.loadingMessage}>Lade erhaltene Likes...</div>;
    }

    if (error) {
        return <div className={styles.errorMessage}>{error}</div>;
    }

    if (!receivedLikes || receivedLikes.length === 0) {
        return (
            <div className={styles.dashboardContainer}>
                <h1 className={styles.dashboardTitle}>Erhaltene Likes</h1>
                <div className={styles.backLinkContainer}>
                    <Link to="/userdashboard" className={styles.backLink}>
                        &larr; Zurück zum Dashboard
                    </Link>
                </div>
                <p className={styles.infoMessage}>Du hast noch keine Likes erhalten.</p>
            </div>
        );
    }

    return (
        <div className={styles.dashboardContainer}>
            <h1 className={styles.dashboardTitle}>Erhaltene Likes</h1>
            <div className={styles.backLinkContainer}>
                <Link to="/userdashboard" className={styles.backLink}>
                    &larr; Zurück zum Dashboard
                </Link>
            </div>

            <div className={styles.suggestionGrid}>
                {receivedLikes.map(like => (
                    <div key={like.id} className={styles.favoriteCard}>
                        <Link to={`/users/${like.user}/profile`} className={styles.suggestionCardLink}>
                            <div className={styles.suggestionCard}>
                                <div className={styles.profilePicContainer}>
                                    {like.profile_picture_url ? (
                                        <img 
                                            src={like.profile_picture_url} 
                                            alt={`Profilbild von ${like.username}`} 
                                            className={styles.profilePic} 
                                        />
                                    ) : (
                                        <div className={styles.profilePicPlaceholder}>?</div>
                                    )}
                                </div>
                                <div className={styles.userInfo}>
                                    <span className={styles.username}>{like.username}</span>
                                </div>
                            </div>
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ReceivedLikesPage;
