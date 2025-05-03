// frontend/src/components/NotificationCenter.jsx
import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext.jsx';
import { Link } from 'react-router-dom';

function NotificationCenter() {
  const { authToken } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Benachrichtigungen laden
  useEffect(() => {
    if (!authToken) return;
    
    const fetchNotifications = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch('http://127.0.0.1:8000/api/notifications/', {
          headers: { 
            'Authorization': `Token ${authToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          // Überprüfen, ob die Daten paginiert sind
          if (data.results && Array.isArray(data.results)) {
            setNotifications(data.results);
            setUnreadCount(data.results.filter(n => !n.is_read).length);
          } else if (Array.isArray(data)) {
            setNotifications(data);
            setUnreadCount(data.filter(n => !n.is_read).length);
          } else {
            console.error("Unerwartetes Datenformat:", data);
            setError("Unerwartetes Datenformat vom Server erhalten.");
            setNotifications([]);
            setUnreadCount(0);
          }
        } else {
          let errorMsg = `Fehler ${response.status}`;
          try {
            const errorData = await response.json();
            errorMsg = errorData.detail || JSON.stringify(errorData);
          } catch (e) {
            // Ignorieren, wenn keine JSON-Antwort
          }
          setError(`Benachrichtigungen konnten nicht geladen werden: ${errorMsg}`);
        }
      } catch (err) {
        setError("Netzwerkfehler beim Laden der Benachrichtigungen.");
        console.error("Fehler beim Laden der Benachrichtigungen:", err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchNotifications();
    // Polling alle 30 Sekunden
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [authToken]);
  
  // Als gelesen markieren
  const markAsRead = async (id) => {
    if (!authToken) return;
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/notifications/${id}/read/`, {
        method: 'POST',
        headers: { 
          'Authorization': `Token ${authToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setNotifications(notifications.map(n => 
          n.id === id ? { ...n, is_read: true } : n
        ));
        setUnreadCount(prev => prev - 1);
      } else {
        console.error(`Fehler beim Markieren der Benachrichtigung als gelesen: ${response.status}`);
      }
    } catch (err) {
      console.error("Netzwerkfehler beim Markieren der Benachrichtigung als gelesen:", err);
    }
  };
  
  // Alle als gelesen markieren
  const markAllAsRead = async () => {
    if (!authToken || unreadCount === 0) return;
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/notifications/read-all/', {
        method: 'POST',
        headers: { 
          'Authorization': `Token ${authToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setNotifications(notifications.map(n => ({ ...n, is_read: true })));
        setUnreadCount(0);
      } else {
        console.error(`Fehler beim Markieren aller Benachrichtigungen als gelesen: ${response.status}`);
      }
    } catch (err) {
      console.error("Netzwerkfehler beim Markieren aller Benachrichtigungen als gelesen:", err);
    }
  };
  
  // Benachrichtigungstyp zu Icon und Link zuordnen
  const getNotificationDetails = (notification) => {
    switch (notification.type) {
      case 'like':
        // Prüfen, ob sender_details und id vorhanden sind
        if (notification.sender_details && notification.sender_details.pk) {
          return {
            icon: '❤️',
            link: `/users/${notification.sender_details.pk}/profile`,
            action: () => markAsRead(notification.id)
          };
        } else {
          console.warn('Sender details missing in notification:', notification);
          return {
            icon: '❤️',
            link: '/userdashboard', // Fallback zur Dashboard-Seite
            action: () => markAsRead(notification.id)
          };
        }
      case 'message':
        // Prüfen, ob sender_details und id vorhanden sind
        if (notification.sender_details && notification.sender_details.pk) {
          return {
            icon: '✉️',
            link: `/chat/${notification.sender_details.pk}`,
            action: () => markAsRead(notification.id)
          };
        } else {
          console.warn('Sender details missing in notification:', notification);
          return {
            icon: '✉️',
            link: '/conversations', // Fallback zur Konversationsübersicht
            action: () => markAsRead(notification.id)
          };
        }
      case 'system':
      default:
        return {
          icon: 'ℹ️',
          link: '#',
          action: () => markAsRead(notification.id)
        };
    }
  };
  
  // Formatierung des Zeitstempels
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Styles
  const styles = {
    container: {
      position: 'relative',
      display: 'inline-block'
    },
    button: {
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      fontSize: '1.5rem',
      position: 'relative',
      padding: '0 0.5rem'
    },
    badge: {
      position: 'absolute',
      top: '-5px',
      right: '0',
      backgroundColor: '#ff4757',
      color: 'white',
      borderRadius: '50%',
      padding: '0.1rem 0.3rem',
      fontSize: '0.7rem',
      fontWeight: 'bold'
    },
    dropdown: {
      position: 'absolute',
      right: '0',
      top: '100%',
      width: '300px',
      maxHeight: '400px',
      overflowY: 'auto',
      backgroundColor: '#9c88ff20', // Leichter Lila-Ton mit Transparenz
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
      borderRadius: '4px',
      zIndex: 1000,
      border: '1px solid #9c88ff40' // Subtiler Lila-Rahmen
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.5rem 1rem',
      borderBottom: '1px solid #9c88ff40', // Lila-Ton für den Rahmen
      backgroundColor: '#9c88ff30' // Etwas dunklerer Lila-Ton für den Header
    },
    title: {
      margin: '0',
      fontSize: '1rem',
      fontWeight: 'bold',
      color: '#ffffff' // Weiße Farbe für bessere Lesbarkeit auf Lila-Hintergrund
    },
    markAllButton: {
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      color: '#6c5ce7', // Lila-Ton für den Button
      fontSize: '0.8rem',
      padding: '0.2rem 0.5rem'
    },
    list: {
      listStyle: 'none',
      padding: '0',
      margin: '0'
    },
    item: {
      padding: '0.75rem 1rem',
      borderBottom: '1px solid #9c88ff30', // Lila-Ton für den Rahmen
      display: 'flex',
      alignItems: 'flex-start',
      cursor: 'pointer',
      transition: 'background-color 0.2s'
    },
    unread: {
      backgroundColor: '#9c88ff15' // Sehr leichter Lila-Ton für ungelesene Benachrichtigungen
    },
    icon: {
      marginRight: '0.75rem',
      fontSize: '1.2rem'
    },
    content: {
      flex: 1
    },
    message: {
      margin: '0 0 0.25rem 0',
      fontSize: '0.9rem',
      color: '#ffffff' // Weiße Farbe für bessere Lesbarkeit auf Lila-Hintergrund
    },
    timestamp: {
      color: '#6c5ce780', // Lila-Ton mit Transparenz für den Zeitstempel
      fontSize: '0.75rem'
    },
    empty: {
      padding: '1rem',
      textAlign: 'center',
      color: '#6c5ce780' // Lila-Ton mit Transparenz
    },
    error: {
      padding: '1rem',
      textAlign: 'center',
      color: '#e74c3c'
    },
    loading: {
      padding: '1rem',
      textAlign: 'center',
      color: '#6c5ce780' // Lila-Ton mit Transparenz
    }
  };
  
  // Wenn nicht eingeloggt, nichts anzeigen
  if (!authToken) return null;
  
  return (
    <div style={styles.container}>
      <button 
        style={styles.button} 
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Benachrichtigungen"
      >
        🔔
        {unreadCount > 0 && (
          <span style={styles.badge}>{unreadCount}</span>
        )}
      </button>
      
      {isOpen && (
        <div style={styles.dropdown}>
          <div style={styles.header}>
            <h3 style={styles.title}>Benachrichtigungen</h3>
            {unreadCount > 0 && (
              <button 
                style={styles.markAllButton}
                onClick={markAllAsRead}
              >
                Alle als gelesen markieren
              </button>
            )}
          </div>
          
          {isLoading ? (
            <div style={styles.loading}>Lade Benachrichtigungen...</div>
          ) : error ? (
            <div style={styles.error}>{error}</div>
          ) : notifications.filter(n => !n.is_read).length === 0 ? (
            <div style={styles.empty}>Keine ungelesenen Benachrichtigungen</div>
          ) : (
            <ul style={styles.list}>
              {notifications.filter(n => !n.is_read).map(notification => {
                const { icon, link, action } = getNotificationDetails(notification);
                return (
                  <li 
                    key={notification.id} 
                    style={{
                      ...styles.item,
                      ...(notification.is_read ? {} : styles.unread)
                    }}
                  >
                    <div style={styles.icon}>{icon}</div>
                    <div style={styles.content}>
                      <Link 
                        to={link} 
                        style={{ textDecoration: 'none', color: 'inherit' }}
                        onClick={action}
                      >
                        <p style={styles.message}>{notification.content}</p>
                        <span style={styles.timestamp}>
                          {formatTimestamp(notification.created_at)}
                        </span>
                      </Link>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default NotificationCenter;
