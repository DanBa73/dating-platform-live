// frontend/src/components/UnreadIndicator.jsx
import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext.jsx';

// Stil für den gelben Punkt (gleiche Farbe wie die Glocke)
const indicatorStyle = {
  display: 'inline-block',
  width: '8px',
  height: '8px',
  borderRadius: '50%',
  backgroundColor: '#f1c40f', // Gelbe Farbe wie die Glocke
  marginLeft: '5px',
  position: 'relative',
  top: '-1px'
};

function UnreadIndicator() {
  const [hasUnread, setHasUnread] = useState(false);
  const { authToken } = useContext(AuthContext);
  
  useEffect(() => {
    // Funktion zum Abrufen der unbeantworteten Nachrichten
    const checkUnreadMessages = async () => {
      if (!authToken) return;
      
      try {
        const response = await fetch('http://127.0.0.1:8000/api/messaging/conversations/?unread=true', {
          method: 'GET',
          headers: {
            'Authorization': `Token ${authToken}`,
            'Content-Type': 'application/json',
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          // Wenn es unbeantwortete Nachrichten gibt, setzen wir hasUnread auf true
          setHasUnread(data.length > 0);
        } else {
          console.error('Failed to fetch unread messages');
        }
      } catch (error) {
        console.error('Error checking unread messages:', error);
      }
    };
    
    // Beim ersten Laden prüfen
    checkUnreadMessages();
    
    // Alle 30 Sekunden aktualisieren
    const intervalId = setInterval(checkUnreadMessages, 30000);
    
    // Cleanup beim Unmount
    return () => clearInterval(intervalId);
  }, [authToken]);
  
  // Wenn keine ungelesenen Nachrichten vorhanden sind, nichts rendern
  if (!hasUnread) return null;
  
  // Ansonsten den roten Punkt rendern
  return <span style={indicatorStyle} title="Unbeantwortete Nachrichten"></span>;
}

export default UnreadIndicator;
