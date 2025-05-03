// frontend/src/pages/FavoritesPage.jsx
import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './UserDashboardPage.module.css'; // Wir verwenden die gleichen Styles wie das Dashboard

function FavoritesPage() {
    const { authToken } = useContext(AuthContext);
    const [favorites, setFavorites] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Laden der Favoriten
    useEffect(() => {
        const fetchFavorites = async () => {
            if (!authToken) return;

            setIsLoading(true);
            setError(null);

            try {
                const response = await fetch('http://127.0.0.1:8000/api/accounts/likes/', {
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
                        setFavorites(data.results);
                    } else if (Array.isArray(data)) {
                        // Wenn die Daten bereits ein Array sind
                        setFavorites(data);
                    } else {
                        // Wenn die Daten weder paginiert noch ein Array sind
                        console.error("Unerwartetes Datenformat:", data);
                        setError("Unerwartetes Datenformat vom Server erhalten.");
                        setFavorites([]);
                    }
                } else {
                    let errorMsg = `Fehler ${response.status}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.detail || JSON.stringify(errorData);
                    } catch (e) {
                        // Ignorieren, wenn keine JSON-Antwort
                    }
                    setError(`Favoriten konnten nicht geladen werden: ${errorMsg}`);
                }
            } catch (err) {
                setError("Netzwerkfehler beim Laden der Favoriten.");
                console.error("Fehler beim Laden der Favoriten:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchFavorites();
    }, [authToken]);

    // Handler zum Entfernen eines Favoriten
    const handleRemoveFavorite = async (userId) => {
        if (!authToken) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/accounts/users/${userId}/like/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Favorit aus der Liste entfernen
                setFavorites(favorites.filter(fav => fav.liked_user !== userId));
            } else {
                console.error('Fehler beim Entfernen des Favoriten:', response.status);
                // Optional: Fehlermeldung anzeigen
            }
        } catch (err) {
            console.error('Netzwerkfehler beim Entfernen des Favoriten:', err);
            // Optional: Fehlermeldung anzeigen
        }
    };

    // Render-Funktionen
    if (isLoading) {
        return <div className={styles.loadingMessage}>Lade Favoriten...</div>;
    }

    if (error) {
        return <div className={styles.errorMessage}>{error}</div>;
    }

    if (!favorites || favorites.length === 0) {
        return (
            <div className={styles.dashboardContainer}>
                <h1 className={styles.dashboardTitle}>Meine Favoriten</h1>
                <div className={styles.backLinkContainer}>
                    <Link to="/userdashboard" className={styles.backLink}>
                        &larr; Zurück zum Dashboard
                    </Link>
                </div>
                <p className={styles.infoMessage}>Du hast noch keine Favoriten hinzugefügt.</p>
            </div>
        );
    }

    return (
        <div className={styles.dashboardContainer}>
            <h1 className={styles.dashboardTitle}>Meine Favoriten</h1>
            <div className={styles.backLinkContainer}>
                <Link to="/userdashboard" className={styles.backLink}>
                    &larr; Zurück zum Dashboard
                </Link>
            </div>

            <div className={styles.suggestionGrid}>
                {favorites.map(favorite => (
                    <div key={favorite.id} className={styles.favoriteCard}>
                        <Link to={`/users/${favorite.liked_user}/profile`} className={styles.suggestionCardLink}>
                            <div className={styles.suggestionCard}>
                                <div className={styles.profilePicContainer}>
                                    {favorite.profile_picture_url ? (
                                        <img 
                                            src={favorite.profile_picture_url} 
                                            alt={`Profilbild von ${favorite.username}`} 
                                            className={styles.profilePic} 
                                        />
                                    ) : (
                                        <div className={styles.profilePicPlaceholder}>?</div>
                                    )}
                                </div>
                                <div className={styles.userInfo}>
                                    <span className={styles.username}>{favorite.username}</span>
                                </div>
                            </div>
                        </Link>
                        <button 
                            onClick={() => handleRemoveFavorite(favorite.liked_user)} 
                            className={styles.removeFavoriteButton}
                            title="Favorit entfernen"
                        >
                            ❌
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default FavoritesPage;
