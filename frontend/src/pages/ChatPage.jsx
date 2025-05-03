// frontend/src/pages/ChatPage.jsx (mit Sende-Logik)

import React, { useState, useEffect, useContext, useCallback, useRef } from 'react'; // useRef hinzugefügt
import { useParams, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import Layout from '../components/Layout';
import { FiArrowLeft, FiSend, FiSmile, FiImage, FiPaperclip, FiX } from 'react-icons/fi';
import styles from './ChatPage.module.css';

// Liste häufig verwendeter Emojis
const commonEmojis = [
  '😊', '😂', '❤️', '👍', '😍', 
  '😘', '🥰', '😎', '🙌', '🤔',
  '😢', '😭', '🥺', '😡', '🔥',
  '💋', '💕', '💯', '🎉', '👏'
];

// Hilfsfunktion zur Berechnung des Alters aus dem Geburtsdatum
const calculateAge = (birthDateStr) => {
  if (!birthDateStr) return null;
  
  try {
    const birthDate = new Date(birthDateStr);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age >= 0 ? age : null;
  } catch (e) {
    console.error("Fehler bei der Altersberechnung:", e);
    return null;
  }
};

function ChatPage() {
  // Profilbild-Platzhalter URL
  const defaultProfileImage = "https://via.placeholder.com/150?text=?";
  const { otherUserId } = useParams();
  const { authToken, user } = useContext(AuthContext);

  const [messages, setMessages] = useState([]);
  const [otherUserName, setOtherUserName] = useState('');
  const [otherUserProfilePic, setOtherUserProfilePic] = useState(null);
  const [currentUserProfilePic, setCurrentUserProfilePic] = useState(null);
  const [otherUserData, setOtherUserData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [lightboxImage, setLightboxImage] = useState(null); // State für die Lightbox
  const [pollingInterval] = useState(10000); // 10 Sekunden Polling-Intervall
  const pollingTimerRef = useRef(null); // Referenz für den Timer
  const messageListRef = useRef(null); // Referenz für die Nachrichtenliste
  const emojiPickerRef = useRef(null); // Referenz für den Emoji-Picker
  const fileInputRef = useRef(null); // Referenz für den Datei-Input
  
  // Funktion zum Scrollen zum Ende der Nachrichtenliste
  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  };
  
  // Funktion zum Hinzufügen eines Emojis zur Nachricht
  const onEmojiClick = (emoji) => {
    setNewMessage(prevMessage => prevMessage + emoji);
    setShowEmojiPicker(false); // Emoji-Picker nach Auswahl schließen
  };
  
  // Funktion zum Umschalten des Emoji-Pickers
  const toggleEmojiPicker = () => {
    setShowEmojiPicker(prevState => !prevState);
  };
  
  // Funktion zum Öffnen des Datei-Dialogs
  const handleImageButtonClick = () => {
    fileInputRef.current.click();
  };
  
  // Funktion zum Verarbeiten der ausgewählten Datei
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Überprüfen, ob es sich um ein Bild handelt
      if (!file.type.startsWith('image/')) {
        setUploadError('Bitte wähle eine Bilddatei aus.');
        return;
      }
      
      // Größenbeschränkung (z.B. 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setUploadError('Das Bild darf nicht größer als 5MB sein.');
        return;
      }
      
      setSelectedImage(file);
      setUploadError(null);
    }
  };
  
  // Funktion zum Hochladen des Bildes
  const uploadImage = async (messageId) => {
    if (!selectedImage || !authToken) return;
    
    setIsUploading(true);
    setUploadError(null);
    
    const formData = new FormData();
    formData.append('file', selectedImage);
    formData.append('message_id', messageId);
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/messaging/upload-attachment/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${authToken}`
        },
        body: formData
      });
      
      if (response.ok) {
        console.log('Bild erfolgreich hochgeladen');
      } else {
        const errorData = await response.json();
        setUploadError(errorData.error || 'Fehler beim Hochladen des Bildes');
        console.error('Fehler beim Hochladen des Bildes:', errorData);
      }
    } catch (error) {
      console.error('Fehler beim Hochladen des Bildes:', error);
      setUploadError('Netzwerkfehler beim Hochladen des Bildes');
    } finally {
      setIsUploading(false);
      // Stellen Sie sicher, dass das Bild aus der Vorschau entfernt wird, auch wenn ein Fehler auftritt
      setSelectedImage(null);
    }
  };
  
  // Funktion zum Schließen des Emoji-Pickers beim Klicken außerhalb
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target)) {
        setShowEmojiPicker(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  

  // --- fetchMessages jetzt als useCallback definiert ---
  // Damit kann sie sicher in useEffect und handleSendMessage verwendet werden.
  const fetchMessages = useCallback(async () => {
    // Verhindern, wenn kein Token oder keine UserID da ist
    if (!authToken || !otherUserId) {
        setError("Nachrichten können nicht ohne Authentifizierung oder Benutzer-ID abgerufen werden.");
        setIsLoading(false);
        return;
    }

    console.log("fetchMessages Funktion gestartet für Benutzer:", otherUserId);
    setIsLoading(true); // Setze Loading beim Start des Fetch
    setError(null);     // Fehler zurücksetzen

    try {
      const apiUrl = `http://127.0.0.1:8000/api/messaging/conversation-with-attachments/${otherUserId}/`;
      console.log("Versuche Daten abzurufen von:", apiUrl);

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Token ${authToken}`,
          'Content-Type': 'application/json',
        },
      });
      console.log("Antwort erhalten, Status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("Nachrichten erfolgreich abgerufen:", data);
        setMessages(data);
        // Verzögertes Scrollen zum Ende, um sicherzustellen, dass die Nachrichten gerendert wurden
        setTimeout(scrollToBottom, 100);
        
        // Wenn Benutzerdaten in der Antwort enthalten sind
        if (data.length > 0 && data[0].recipient) {
          // Bestimme, welcher Benutzer der andere ist (basierend auf der otherUserId)
          const otherUser = data[0].sender.id === parseInt(otherUserId, 10) 
            ? data[0].sender 
            : data[0].recipient;
          
          // Bestimme, welcher Benutzer der aktuelle ist (der nicht der andere ist)
          const currentUser = data[0].sender.id === parseInt(otherUserId, 10) 
            ? data[0].recipient 
            : data[0].sender;
          
          console.log("Anderer Benutzer:", otherUser);
          console.log("Aktueller Benutzer:", currentUser);
          
          // Speichere alle Daten des anderen Benutzers
          setOtherUserData(otherUser);
          setOtherUserName(otherUser.username || `Benutzer ${otherUserId}`);
          
          // Profilbild-URLs extrahieren und loggen
          const otherProfilePicUrl = otherUser.profile_picture_url;
          const currentProfilePicUrl = currentUser.profile_picture_url;
          
          console.log("Profilbild-URL des anderen Benutzers:", otherProfilePicUrl);
          console.log("Profilbild-URL des aktuellen Benutzers:", currentProfilePicUrl);
          
          setOtherUserProfilePic(otherProfilePicUrl || null);
          setCurrentUserProfilePic(currentProfilePicUrl || null);
          
          // Online-Status basierend auf der Aktivität setzen
          // Wenn die letzte Nachricht vom anderen Benutzer innerhalb der letzten 30 Minuten war, gilt er als online
          const lastMessageFromOtherUser = data
            .filter(msg => msg.sender.id === parseInt(otherUserId, 10))
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
          
          if (lastMessageFromOtherUser) {
            const lastMessageTime = new Date(lastMessageFromOtherUser.timestamp);
            const thirtyMinutesAgo = new Date();
            thirtyMinutesAgo.setMinutes(thirtyMinutesAgo.getMinutes() - 30);
            
            setIsOnline(lastMessageTime > thirtyMinutesAgo);
          } else {
            // Zufällige Online-Wahrscheinlichkeit für neue Kontakte
            setIsOnline(Math.random() > 0.2);
          }
        } else {
          setOtherUserName(`Benutzer ${otherUserId}`);
        }
      } else {
        let errorMsg = 'Fehler beim Laden der Nachrichten.';
        try {
          const errorData = await response.json();
          console.error('Fehler beim Abrufen der Nachrichten (Backend-Antwort):', errorData);
          errorMsg = errorData.detail || errorData.error || `Error ${response.status}`;
        } catch (e) {
           console.error('Fehlerantwort konnte nicht verarbeitet werden:', e);
           errorMsg = `Error: ${response.status} ${response.statusText}`;
        }
        setError(errorMsg);
      }
    } catch (err) {
      console.error("Netzwerkfehler beim Abrufen der Nachrichten:", err);
      setError("Netzwerkfehler. Bitte versuche es erneut.");
    } finally {
      console.log("fetchMessages Funktion beendet.");
      setIsLoading(false); // Loading beenden, egal was passiert
    }
  }, [authToken, otherUserId]); // Abhängigkeiten für useCallback und useEffect

  // Initialer Fetch beim Laden der Komponente
  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]); // fetchMessages ist eine Abhängigkeit

  // Polling-Mechanismus für automatische Aktualisierung
  useEffect(() => {
    // Starte das Polling nur, wenn authToken und otherUserId vorhanden sind
    if (authToken && otherUserId) {
      console.log("Starte Polling für neue Nachrichten alle", pollingInterval, "ms");
      
      // Bereinige vorherigen Timer, falls vorhanden
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
      }
      
      // Setze neuen Timer
      pollingTimerRef.current = setInterval(() => {
        console.log("Polling: Rufe neue Nachrichten ab...");
        fetchMessages();
      }, pollingInterval);
      
      // Bereinigungsfunktion, die beim Unmounten der Komponente aufgerufen wird
      return () => {
        console.log("Bereinige Polling-Timer");
        if (pollingTimerRef.current) {
          clearInterval(pollingTimerRef.current);
        }
      };
    }
  }, [authToken, otherUserId, pollingInterval, fetchMessages]);

  // --- handleSendMessage mit API-Call implementiert ---
  const handleSendMessage = async (event) => {
    event.preventDefault();
    const contentToSend = newMessage.trim(); // Leerzeichen entfernen
    if (!contentToSend && !selectedImage) return; // Nicht senden, wenn weder Text noch Bild vorhanden
    if (!authToken) { setError("Nachricht kann nicht gesendet werden, du bist nicht eingeloggt."); return; }

    console.log("Versuche Nachricht zu senden:", contentToSend);
    // Optional: Fehler kurz zurücksetzen, damit alte Fehler verschwinden
    // setError(null);

    const apiUrl = 'http://127.0.0.1:8000/api/messaging/send/';
    const payload = {
        // Stelle sicher, dass die ID als Zahl gesendet wird
        recipient_id: parseInt(otherUserId, 10),
        content: contentToSend || (selectedImage ? "Bild gesendet" : "")
    };

    try {
         const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
              'Authorization': `Token ${authToken}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
         });

         if (response.ok) {
            console.log("Nachricht erfolgreich über API gesendet.");
            setNewMessage(''); // Eingabefeld leeren
            
            // Wenn ein Bild ausgewählt wurde, lade es hoch
            if (selectedImage) {
              try {
                const responseData = await response.json();
                if (responseData && responseData.id) {
                  await uploadImage(responseData.id);
                }
              } catch (error) {
                console.error('Fehler beim Verarbeiten der Antwort oder Hochladen des Bildes:', error);
                setUploadError('Fehler beim Hochladen des Bildes');
              } finally {
                // Stellen Sie sicher, dass das Bild aus der Vorschau entfernt wird, auch wenn ein Fehler auftritt
                setSelectedImage(null);
              }
            }
            
            // Nachrichtenliste neu laden, um die neue Nachricht anzuzeigen
            fetchMessages();
         } else {
            // Fehler beim Senden (z.B. nicht genug Coins)
            let errorMsg = 'Fehler beim Senden der Nachricht.';
             try {
               const errorData = await response.json();
               console.error('Nachricht senden fehlgeschlagen (Backend-Antwort):', errorData);
               errorMsg = errorData.error || errorData.detail || `Error ${response.status}`;
             } catch (e) {
               console.error('Fehlerantwort beim Senden konnte nicht verarbeitet werden:', e);
               errorMsg = `Error: ${response.status} ${response.statusText}`;
             }
             setError(errorMsg); // Zeige Sendefehler an
         }

    } catch(error) {
        console.error("Netzwerkfehler beim Senden der Nachricht:", error);
        setError('Netzwerkfehler beim Senden. Bitte versuche es erneut.');
    }
  };

  // --- JSX Rendering ---
  if (isLoading && messages.length === 0) { // Zeige Loading nur beim initialen Laden
    return (
      <div className={styles.loadingMessage}>Chat wird geladen...</div>
    );
  }
  
  // Zeige Fehler nur, wenn *keine* Nachrichten geladen wurden ODER beim Senden
  // (damit der Chat bei einem Sendefehler nicht verschwindet)
  if (error && messages.length === 0) {
    return (
      <div className={styles.errorMessage}>Fehler beim Laden des Chats: {error}</div>
    );
  }

  return (
    <div className={styles.outerContainer}>
      {/* Linke Seite - Anderer Benutzer (Fake-User) */}
      <div className={styles.sidePanel}>
        {/* Profilbild */}
        <div className={styles.profileContainer}>
          <img 
            src={otherUserProfilePic || defaultProfileImage} 
            alt={`${otherUserName} Profilbild`} 
            className={styles.profileImage} 
          />
          {isOnline && <span className={styles.onlineIndicator}></span>}
        </div>
        
        {/* Benutzerinfo */}
        <div className={styles.userInfoPanel}>
          <h3>{otherUserName}</h3>
          <div className={styles.userDetailsList}>
            {otherUserData?.age && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Alter:</span>
                <span className={styles.detailValue}>{otherUserData.age} Jahre</span>
              </div>
            )}
            {otherUserData?.city && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Stadt:</span>
                <span className={styles.detailValue}>{otherUserData.city}</span>
              </div>
            )}
            {otherUserData?.gender && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Geschlecht:</span>
                <span className={styles.detailValue}>
                  {otherUserData.gender === 'MALE' ? 'Männlich' : 
                   otherUserData.gender === 'FEMALE' ? 'Weiblich' : 
                   otherUserData.gender}
                </span>
              </div>
            )}
            {otherUserData?.seeking && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Sucht:</span>
                <span className={styles.detailValue}>
                  {otherUserData.seeking === 'MALE' ? 'Männer' : 
                   otherUserData.seeking === 'FEMALE' ? 'Frauen' : 
                   otherUserData.seeking}
                </span>
              </div>
            )}
          </div>
          {otherUserData?.about_me && (
            <div className={styles.aboutMePanel}>
              <h4>Über mich</h4>
              <p>{otherUserData.about_me}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Chat-Container in der Mitte */}
      <div className={styles.chatContainer}>
        <div className={styles.chatHeader}>
          <Link to="/userdashboard" className={styles.backButton}>
            <FiArrowLeft size={20} />
            <span>Zurück zum Dashboard</span>
          </Link>
          
          <h2>{otherUserName}</h2>
        </div>
        {/* Zeige Sendefehler oberhalb der Liste, wenn Nachrichten schon da sind */}
        {error && messages.length > 0 && <p className={styles.errorMessage}>Fehler: {error}</p>}
        <div className={styles.messageList} ref={messageListRef}>
          {messages.length === 0 && !isLoading ? (
            <p className={styles.infoMessage}>Noch keine Nachrichten. Starte die Unterhaltung!</p>
          ) : (
            messages.map(message => {
              // Bestimme, ob es meine Nachricht ist oder vom anderen User
              const isMyMessage = message.sender.id !== parseInt(otherUserId, 10);
              const messageClass = isMyMessage ? styles.myMessage : styles.theirMessage;
              
              return (
                <div key={message.id} className={`${styles.messageItem} ${messageClass}`}>
                  <div className={styles.messageContent}>{message.content}</div>
                  
                  {/* Anzeige von Anhängen, falls vorhanden */}
                  {message.attachments && message.attachments.length > 0 && (
                    <div className={styles.attachmentContainer}>
                      {message.attachments.map((attachment, index) => (
                        <div key={index} className={styles.attachment}>
                          {attachment.file_type.startsWith('image/') ? (
                            <img 
                              src={attachment.file_url} 
                              alt="Bildanhang" 
                              className={styles.attachmentImage}
                              onClick={() => setLightboxImage(attachment.file_url)}
                            />
                          ) : (
                            <a 
                              href={attachment.file_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className={styles.attachmentLink}
                            >
                              Anhang herunterladen
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className={styles.messageTimestamp}>
                    {new Date(message.timestamp).toLocaleString('de-DE', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Eingabeformular mit CSS-Modulen */}
        <form onSubmit={handleSendMessage} className={styles.inputForm}>
          <div className={styles.inputContainer}>
            <div className={styles.inputButtons}>
              <button 
                type="button" 
                className={styles.emojiButton} 
                onClick={toggleEmojiPicker}
                aria-label="Emoji einfügen"
              >
                <FiSmile size={20} />
              </button>
              
              <button
                type="button"
                className={styles.imageButton}
                onClick={handleImageButtonClick}
                aria-label="Bild senden"
              >
                <FiImage size={20} />
              </button>
              
              {/* Versteckter Datei-Input */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                style={{ display: 'none' }}
              />
            </div>
            
            <input 
              type="text" 
              value={newMessage} 
              onChange={(e) => setNewMessage(e.target.value)} 
              placeholder={selectedImage ? "Bild wird gesendet..." : "Nachricht eingeben..."} 
              className={styles.messageInput} 
            />
            
            {/* Vorschau des ausgewählten Bildes */}
            {selectedImage && (
              <div className={styles.imagePreviewContainer}>
                <div className={styles.imagePreview}>
                  <img 
                    src={URL.createObjectURL(selectedImage)} 
                    alt="Vorschau" 
                  />
                  <button 
                    type="button" 
                    className={styles.removeImageButton}
                    onClick={() => setSelectedImage(null)}
                  >
                    ×
                  </button>
                </div>
              </div>
            )}
            
            {showEmojiPicker && (
              <div className={styles.emojiPickerContainer} ref={emojiPickerRef}>
                <div className={styles.emojiGrid}>
                  {commonEmojis.map((emoji, index) => (
                    <button
                      key={index}
                      type="button"
                      className={styles.emojiButton}
                      onClick={() => onEmojiClick(emoji)}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <button type="submit" className={styles.sendButton}>
            Senden
            <FiSend size={16} style={{ marginLeft: '6px' }} />
          </button>
        </form>
      </div>
      
      {/* Rechte Seite - Aktueller Benutzer (Echter User) */}
      <div className={styles.sidePanel}>
        {/* Profilbild */}
        <div className={styles.profileContainer}>
          <img 
            src={currentUserProfilePic || defaultProfileImage} 
            alt="Mein Profilbild" 
            className={styles.profileImage} 
          />
        </div>
        
        {/* Benutzerinfo des echten Users */}
        <div className={styles.userInfoPanel}>
          <h3>Mein Profil</h3>
          <div className={styles.userDetailsList}>
            {user?.birth_date && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Alter:</span>
                <span className={styles.detailValue}>
                  {calculateAge(user.birth_date)} Jahre
                </span>
              </div>
            )}
            {user?.city && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Stadt:</span>
                <span className={styles.detailValue}>{user.city}</span>
              </div>
            )}
            {user?.gender && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Geschlecht:</span>
                <span className={styles.detailValue}>
                  {user.gender === 'MALE' ? 'Männlich' : 
                   user.gender === 'FEMALE' ? 'Weiblich' : 
                   user.gender}
                </span>
              </div>
            )}
            {user?.seeking && (
              <div className={styles.userDetailItem}>
                <span className={styles.detailLabel}>Suche:</span>
                <span className={styles.detailValue}>
                  {user.seeking === 'MALE' ? 'Männer' : 
                   user.seeking === 'FEMALE' ? 'Frauen' : 
                   user.seeking}
                </span>
              </div>
            )}
          </div>
          {user?.about_me && (
            <div className={styles.aboutMePanel}>
              <h4>Über mich</h4>
              <p>{user.about_me}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Lightbox für Bildanzeige */}
      {lightboxImage && (
        <div className={styles.lightbox} onClick={() => setLightboxImage(null)}>
          <div className={styles.lightboxContent} onClick={(e) => e.stopPropagation()}>
            <img src={lightboxImage} alt="Vergrößertes Bild" className={styles.lightboxImage} />
            <button 
              className={styles.lightboxCloseButton}
              onClick={() => setLightboxImage(null)}
            >
              <FiX size={24} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatPage;
// Ende der Datei ChatPage.jsx (mit Sende-Logik)
