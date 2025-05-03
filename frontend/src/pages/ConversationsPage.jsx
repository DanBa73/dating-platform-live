// frontend/src/pages/ConversationsPage.jsx
import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './ConversationsPage.module.css';

function ConversationsPage() {
    const { authToken } = useContext(AuthContext);
    const [conversations, setConversations] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchConversations = async () => {
            if (!authToken) {
                setError("Sie müssen angemeldet sein, um Ihre Gespräche zu sehen.");
                setIsLoading(false);
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:8000/api/messaging/conversations/', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${authToken}`,
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setConversations(data);
                } else {
                    let errorMsg = 'Fehler beim Laden der Gespräche.';
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.detail || errorData.error || `Fehler ${response.status}`;
                    } catch (e) {
                        errorMsg = `Fehler: ${response.status} ${response.statusText}`;
                    }
                    setError(errorMsg);
                }
            } catch (err) {
                console.error("Netzwerkfehler beim Laden der Gespräche:", err);
                setError("Netzwerkfehler. Bitte versuchen Sie es später erneut.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchConversations();
    }, [authToken]);

    // Formatiert das Datum in ein lesbares Format
    const formatDate = (dateString) => {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('de-DE', options);
    };

    if (isLoading) {
        return <div className={styles.loadingContainer}>Gespräche werden geladen...</div>;
    }

    if (error) {
        return <div className={styles.errorContainer}>{error}</div>;
    }

    return (
        <div className={styles.conversationsContainer}>
            <h1 className={styles.pageTitle}>Meine Gespräche</h1>
            
            {conversations.length === 0 ? (
                <div className={styles.emptyState}>
                    <p>Sie haben noch keine Gespräche.</p>
                    <p>Entdecken Sie Profile und beginnen Sie eine Unterhaltung!</p>
                </div>
            ) : (
                <div className={styles.conversationsList}>
                    {conversations.map((conversation) => (
                        <Link 
                            to={`/chat/${conversation.other_user.id}`}
                            key={conversation.other_user.id}
                            className={`${styles.conversationCard} ${conversation.is_unanswered ? styles.unanswered : ''}`}
                        >
                            <div className={styles.userImageContainer}>
                                {conversation.other_user.profile_picture_url ? (
                                    <img 
                                        src={conversation.other_user.profile_picture_url} 
                                        alt={`${conversation.other_user.username}'s Profilbild`}
                                        className={styles.userImage}
                                    />
                                ) : (
                                    <div className={styles.userImagePlaceholder}>
                                        {conversation.other_user.username.charAt(0).toUpperCase()}
                                    </div>
                                )}
                            </div>
                            
                            <div className={styles.conversationDetails}>
                                <div className={styles.conversationHeader}>
                                    <h3 className={styles.username}>{conversation.other_user.username}</h3>
                                    <span className={styles.timestamp}>{formatDate(conversation.last_message.timestamp)}</span>
                                </div>
                                
                                <p className={styles.messagePreview}>
                                    {conversation.last_message.is_from_user ? 'Sie: ' : ''}
                                    {conversation.last_message.content}
                                </p>
                                
                                {conversation.is_unanswered && (
                                    <div className={styles.unansweredBadge}>Unbeantwortet</div>
                                )}
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}

export default ConversationsPage;
