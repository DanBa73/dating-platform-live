// frontend/src/components/ActivitySummary.jsx
import React, { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';

function ActivitySummary() {
  const { authToken } = useContext(AuthContext);
  const [summary, setSummary] = useState(null);
  const [isVisible, setIsVisible] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (!authToken) return;
    
    const fetchSummary = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch('http://127.0.0.1:8000/api/notifications/summary/', {
          headers: { 
            'Authorization': `Token ${authToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setSummary(data);
          // Nur anzeigen, wenn es ungelesene Benachrichtigungen gibt
          setIsVisible(data.total_unread > 0);
        } else {
          let errorMsg = `Fehler ${response.status}`;
          try {
            const errorData = await response.json();
            errorMsg = errorData.detail || JSON.stringify(errorData);
          } catch (e) {
            // Ignorieren, wenn keine JSON-Antwort
          }
          setError(`Aktivitätsübersicht konnte nicht geladen werden: ${errorMsg}`);
          console.error(`Fehler beim Laden der Aktivitätsübersicht: ${errorMsg}`);
        }
      } catch (err) {
        setError("Netzwerkfehler beim Laden der Aktivitätsübersicht.");
        console.error("Fehler beim Laden der Aktivitätsübersicht:", err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSummary();
  }, [authToken]);
  
  // Styles
  const styles = {
    container: {
      backgroundColor: '#9c88ff20', // Leichter Lila-Ton mit Transparenz
      borderRadius: '8px',
      padding: '1.5rem',
      marginBottom: '2rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      position: 'relative',
      border: '1px solid #9c88ff40' // Subtiler Lila-Rahmen
    },
    title: {
      fontSize: '1.25rem',
      fontWeight: 'bold',
      marginBottom: '1rem',
      color: '#ffffff' // Weiße Farbe für bessere Lesbarkeit auf Lila-Hintergrund
    },
    closeButton: {
      position: 'absolute',
      top: '0.75rem',
      right: '0.75rem',
      background: 'none',
      border: 'none',
      fontSize: '1.25rem',
      cursor: 'pointer',
      color: '#6c5ce7' // Lila-Ton für den Schließen-Button
    },
    summaryItem: {
      display: 'flex',
      alignItems: 'center',
      marginBottom: '0.75rem'
    },
    icon: {
      marginRight: '0.75rem',
      fontSize: '1.25rem'
    },
    text: {
      fontSize: '1rem',
      color: '#ffffff' // Weiße Farbe für bessere Lesbarkeit auf Lila-Hintergrund
    },
    actions: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '0.5rem',
      marginTop: '1rem'
    },
    actionButton: {
      display: 'inline-block',
      padding: '0.5rem 1rem',
      backgroundColor: '#6c5ce7',
      color: 'white',
      borderRadius: '4px',
      textDecoration: 'none',
      fontSize: '0.9rem',
      transition: 'background-color 0.2s'
    },
    loading: {
      padding: '1rem 0',
      color: '#999',
      textAlign: 'center'
    },
    error: {
      padding: '1rem 0',
      color: '#e74c3c',
      textAlign: 'center'
    }
  };
  
  // Wenn nicht eingeloggt, nicht anzeigen
  if (!authToken) return null;
  
  // Wenn keine ungelesenen Benachrichtigungen oder ausgeblendet, nicht anzeigen
  if (!isVisible) return null;
  
  // Wenn noch lädt, Ladeindikator anzeigen
  if (isLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Lade Aktivitätsübersicht...</div>
      </div>
    );
  }
  
  // Wenn Fehler, Fehlermeldung anzeigen
  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>{error}</div>
      </div>
    );
  }
  
  // Wenn keine Zusammenfassung, nichts anzeigen
  if (!summary) return null;
  
  return (
    <div style={styles.container}>
      <button 
        style={styles.closeButton} 
        onClick={() => setIsVisible(false)}
        aria-label="Schließen"
      >
        ×
      </button>
      
      <h2 style={styles.title}>Neue Aktivitäten</h2>
      
      <div>
        {summary.new_likes > 0 && (
          <div style={styles.summaryItem}>
            <span style={styles.icon}>❤️</span>
            <span style={styles.text}>
              Du hast {summary.new_likes} neue{summary.new_likes === 1 ? 'n Like' : ' Likes'} erhalten
            </span>
          </div>
        )}
        
        {summary.unread_messages > 0 && (
          <div style={styles.summaryItem}>
            <span style={styles.icon}>✉️</span>
            <span style={styles.text}>
              Du hast {summary.unread_messages} ungelesene{summary.unread_messages === 1 ? ' Nachricht' : ' Nachrichten'}
            </span>
          </div>
        )}
      </div>
      
      <div style={styles.actions}>
        {summary.new_likes > 0 && (
          <Link to="/received-likes" style={styles.actionButton}>
            Likes anzeigen
          </Link>
        )}
        
        {summary.unread_messages > 0 && (
          <Link to="/conversations" style={styles.actionButton}>
            Nachrichten lesen
          </Link>
        )}
      </div>
    </div>
  );
}

export default ActivitySummary;
