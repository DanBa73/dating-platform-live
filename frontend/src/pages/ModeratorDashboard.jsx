// frontend/src/pages/ModeratorDashboard.jsx
import React, { useState, useEffect, useContext, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext.jsx';
import { Link } from 'react-router-dom';
import { FiFilter, FiMessageSquare, FiArrowLeft } from 'react-icons/fi';
import styles from './ModeratorDashboard.module.css';

function ModeratorDashboard() {
    const { authToken, user } = useContext(AuthContext);
    const [conversations, setConversations] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showUnansweredOnly, setShowUnansweredOnly] = useState(false);

    // Fetch-Funktion mit useCallback und Filter-Logik
    const fetchModeratorConversations = useCallback(async () => {
        console.log(`ModeratorDashboard: Attempting to fetch conversations. Unanswered filter: ${showUnansweredOnly}`);
        setIsLoading(true);
        setError(null);

        if (!authToken) {
            setError("Authentication required.");
            setIsLoading(false);
            return;
        }

        try {
            // Basis-URL
            let apiUrl = `http://127.0.0.1:8000/api/messaging/secure/managed-chats/`;
            // Füge Parameter hinzu, wenn Filter aktiv ist
            if (showUnansweredOnly) {
                apiUrl += `?unanswered=true`;
            }
            console.log("Fetching URL:", apiUrl); // Zeigt die verwendete URL

            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                console.log("ModeratorDashboard: Conversations fetched:", data);
                setConversations(data);
            } else {
                let errorMsg = 'Failed to load conversations.';
                try {
                    const errorData = await response.json();
                    console.error('Error fetching mod conversations (Backend Response):', errorData);
                    errorMsg = errorData.detail || errorData.error || `Error ${response.status}`;
                } catch (e) {
                    errorMsg = `Error: ${response.status} ${response.statusText}`;
                }
                setError(errorMsg);
            }
        } catch (err) {
            console.error("Network error fetching mod conversations:", err);
            setError("Network error. Please try again.");
        } finally {
            setIsLoading(false);
        }
    }, [authToken, showUnansweredOnly]); // Abhängig von Token UND Filter-State!
    // --- ENDE NEU ---

    // useEffect ruft jetzt die useCallback-Funktion auf
    useEffect(() => {
        fetchModeratorConversations();
    }, [fetchModeratorConversations]); // Abhängig von der Funktion selbst

    if (isLoading) { 
        return <div className={styles.loadingMessage}>Moderator Dashboard wird geladen...</div>; 
    }
    
    if (error) { 
        return <div className={styles.errorMessage}>Fehler beim Laden des Dashboards: {error}</div>; 
    }

    return (
        <div className={styles.dashboardContainer}>
            <div className={styles.dashboardHeader}>
                <h1 className={styles.dashboardTitle}>Moderator Dashboard</h1>
                <p className={styles.dashboardSubtitle}>
                    Willkommen, {user?.username || 'Moderator'}! Verwalte Gespräche zwischen echten und Fake-Benutzern.
                </p>
            </div>

            <div className={styles.filterContainer}>
                <label className={styles.filterLabel}>
                    <input
                        type="checkbox"
                        className={styles.filterCheckbox}
                        checked={showUnansweredOnly}
                        onChange={(e) => setShowUnansweredOnly(e.target.checked)}
                    />
                    <FiFilter style={{ marginRight: '0.5rem' }} />
                    Nur unbeantwortete Gespräche anzeigen
                </label>
            </div>

            {conversations.length === 0 ? (
                <div className={styles.emptyMessage}>
                    Keine Gespräche gefunden {showUnansweredOnly ? 'die dem Filter entsprechen' : 'die derzeit Aufmerksamkeit benötigen'}.
                </div>
            ) : (
                <div className={styles.conversationList}>
                    {conversations.map(convo => (
                        <div key={`${convo.real_user.id}-${convo.fake_user.id}`} className={styles.conversationCard}>
                            <p className={styles.conversationHeader}>
                                <FiMessageSquare style={{ marginRight: '0.5rem' }} />
                                {convo.real_user.username} ↔ {convo.fake_user.username}
                            </p>
                            <p className={styles.conversationContent}>
                                "{convo.last_message_content}"
                            </p>
                            <p className={styles.conversationTimestamp}>
                                Letzte Nachricht: {new Date(convo.last_message_timestamp).toLocaleString('de-DE')}
                            </p>
                            <Link 
                                to={`/moderator/chat/${convo.real_user.id}/${convo.fake_user.id}`}
                                className={styles.viewButton}
                            >
                                Ansehen/Antworten
                            </Link>
                        </div>
                    ))}
                </div>
            )}
            
            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', color: '#3498db', textDecoration: 'none' }}>
                    <FiArrowLeft style={{ marginRight: '0.5rem' }} />
                    Zurück zur Hauptseite
                </Link>
            </div>
        </div>
    );
}

export default ModeratorDashboard;
