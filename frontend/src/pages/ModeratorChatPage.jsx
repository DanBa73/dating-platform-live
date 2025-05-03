// frontend/src/pages/ModeratorChatPage.jsx
import React, { useState, useEffect, useContext, useCallback, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import { FiArrowLeft, FiSend, FiSave, FiCpu, FiMessageSquare } from 'react-icons/fi';
import styles from './ModeratorChatPage.module.css';

function ModeratorChatPage() {
    // Ref für die Nachrichtenliste zum automatischen Scrollen
    const messageListRef = useRef(null);
    
    // Funktion zum Scrollen zum Ende der Nachrichtenliste
    const scrollToBottom = () => {
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    };
    const { realUserId, fakeUserId } = useParams();
    const { authToken, user } = useContext(AuthContext);

    // Navigation
    const navigate = useNavigate();

    // Alle States
    const [messages, setMessages] = useState([]);
    const [realUserName, setRealUserName] = useState(`User ${realUserId}`);
    const [fakeUserName, setFakeUserName] = useState(`User ${fakeUserId}`);
    const [isLoading, setIsLoading] = useState(true); // Nachrichten laden
    const [error, setError] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [moderatorNotes, setModeratorNotes] = useState('');
    const [notesLoading, setNotesLoading] = useState(false);
    const [notesError, setNotesError] = useState(null);
    const [notesSaveSuccess, setNotesSaveSuccess] = useState(false);
    const [isSuggesting, setIsSuggesting] = useState(false);
    const [suggestionError, setSuggestionError] = useState(null);
    const [aiSuggestions, setAiSuggestions] = useState([]);
    const [conversationAiMode, setConversationAiMode] = useState('NONE');
    const [modeLoading, setModeLoading] = useState(true);
    const [modeError, setModeError] = useState(null);
    const [realUserProfileData, setRealUserProfileData] = useState(null);
    const [profileLoading, setProfileLoading] = useState(true);
    const [realProfileError, setRealProfileError] = useState(null);
    const [fakeUserProfileData, setFakeUserProfileData] = useState(null);
    const [fakeProfileLoading, setFakeProfileLoading] = useState(true);
    const [fakeProfileError, setFakeProfileError] = useState(null);
    const [unansweredConversations, setUnansweredConversations] = useState([]);
    const [unansweredLoading, setUnansweredLoading] = useState(false);
    const [unansweredError, setUnansweredError] = useState(null);


    // Fetch-Funktionen
    const fetchMessages = useCallback(async () => {
        const parsedRealUserId = parseInt(realUserId, 10); 
        const parsedFakeUserId = parseInt(fakeUserId, 10); 
        
        if (!authToken || isNaN(parsedRealUserId) || isNaN(parsedFakeUserId)) { 
            setError("Cannot fetch messages: Invalid User IDs or Auth token missing."); 
            setIsLoading(false); 
            return; 
        } 
        
        console.log(`ModeratorChatPage: Fetching conversation...`); 
        setIsLoading(true); 
        setError(null); 
        
        try { 
      const apiUrl = `http://127.0.0.1:8000/api/messaging/secure/chat-session/${parsedRealUserId}/${parsedFakeUserId}/`; 
            const response = await fetch(apiUrl, { 
                method: 'GET', 
                headers: { 
                    'Authorization': `Token ${authToken}`, 
                    'Content-Type': 'application/json', 
                } 
            }); 
            
            if (response.ok) { 
                const data = await response.json(); 
                setMessages(data); 
                
                // Verzögertes Scrollen zum Ende, um sicherzustellen, dass die Nachrichten gerendert wurden
                setTimeout(scrollToBottom, 100);
                
                if (data.length > 0) { 
                    const firstMessage = data[0]; 
                    const userA = firstMessage.sender; 
                    const userB = firstMessage.recipient; 
                    const realUser = userA.id === parsedRealUserId ? userA : (userB.id === parsedRealUserId ? userB : null); 
                    const fakeUser = userA.id === parsedFakeUserId ? userA : (userB.id === parsedFakeUserId ? userB : null); 
                    setRealUserName(realUser?.username || `User ${parsedRealUserId}`); 
                    setFakeUserName(fakeUser?.username || `User ${parsedFakeUserId}`); 
                } else { 
                    setRealUserName(`User ${parsedRealUserId}`); 
                    setFakeUserName(`User ${parsedFakeUserId}`); 
                } 
            } else { 
                let errorMsg = 'Failed to load messages.'; 
                try { 
                    const errorData = await response.json(); 
                    console.error('Error fetching messages (Backend Response):', errorData); 
                    errorMsg = errorData.detail || errorData.error || `Error ${response.status}`; 
                } catch (e) { 
                    errorMsg = `Error: ${response.status} ${response.statusText}`; 
                } 
                setError(errorMsg); 
            } 
        } catch (err) { 
            console.error("Network error fetching messages:", err); 
            setError("Network error. Please try again."); 
        } finally { 
            setIsLoading(false); 
        }
    }, [authToken, realUserId, fakeUserId]);
    const fetchNotes = useCallback(async () => {
        const parsedRealUserId = parseInt(realUserId, 10); 
        if (!authToken || isNaN(parsedRealUserId)) { 
            setNotesError("Cannot fetch notes: Invalid Real User ID or Auth token missing."); 
            return; 
        } 
        console.log(`ModeratorChatPage: Fetching notes for user ${parsedRealUserId}...`); 
        setNotesLoading(true); 
        setNotesError(null); 
        setNotesSaveSuccess(false); 
        
        try { 
            // Korrigierte URL für Notizen
            const apiUrl = `http://127.0.0.1:8000/api/accounts/users/${parsedRealUserId}/notes/`; 
            const response = await fetch(apiUrl, { 
                method: 'GET', 
                headers: { 
                    'Authorization': `Token ${authToken}`, 
                    'Content-Type': 'application/json', 
                } 
            }); 
            
            if (response.ok) { 
                const data = await response.json(); 
                setModeratorNotes(data.moderator_notes || ''); 
                console.log(`Notes fetched successfully for user ${parsedRealUserId}.`); 
            } else { 
                let errorMsg = 'Failed to load notes.'; 
                try { 
                    const errorData = await response.json(); 
                    console.error('Error fetching notes (Backend Response):', errorData); 
                    errorMsg = errorData.detail || `Error ${response.status}`; 
                } catch (e) { 
                    errorMsg = `Error: ${response.status} ${response.statusText}`; 
                } 
                setNotesError(errorMsg); 
            } 
        } catch (err) { 
            console.error("Network error fetching notes:", err); 
            setNotesError("Network error fetching notes. Please try again."); 
        } finally { 
            setNotesLoading(false); 
        }
    }, [authToken, realUserId]);
    const fetchConversationAiMode = useCallback(async () => {
        const parsedRealUserId = parseInt(realUserId, 10); const parsedFakeUserId = parseInt(fakeUserId, 10); if (!authToken || isNaN(parsedRealUserId) || isNaN(parsedFakeUserId)) { setModeError("Cannot fetch AI mode: Invalid User IDs or Auth token missing."); return; } console.log(`Workspaceing AI mode for conversation ${parsedRealUserId} <-> ${parsedFakeUserId}`); setModeLoading(true); setModeError(null); const apiUrl = `http://127.0.0.1:8000/api/messaging/chat-preferences/${parsedRealUserId}/${parsedFakeUserId}/`; try { const response = await fetch(apiUrl, { method: 'GET', headers: { 'Authorization': `Token ${authToken}`, 'Content-Type': 'application/json' } }); if (response.ok) { const data = await response.json(); setConversationAiMode(data.ai_mode || 'NONE'); console.log("Conversation AI Mode fetched:", data.ai_mode); } else { let errorMsg = 'Failed to load AI mode.'; try { const errorData = await response.json(); errorMsg = errorData.detail || `Error ${response.status}`; } catch(e) { errorMsg = `Error ${response.status}`; } setModeError(errorMsg); setConversationAiMode('NONE'); } } catch (err) { console.error("Network error fetching AI mode:", err); setModeError("Network error fetching AI mode."); setConversationAiMode('NONE'); } finally { setModeLoading(false); }
    }, [authToken, realUserId, fakeUserId]);
    const fetchRealUserProfile = useCallback(async () => {
        const parsedRealUserId = parseInt(realUserId, 10); 
        if (!authToken || isNaN(parsedRealUserId)) { 
            setRealProfileError("Cannot fetch profile: Invalid Real User ID or Auth token missing."); 
            return; 
        } 
        console.log(`Fetching profile data for real user ${parsedRealUserId}...`); 
        setProfileLoading(true); 
        setRealProfileError(null); 
        
        // Korrigierte URL für Profile
        const apiUrl = `http://127.0.0.1:8000/api/accounts/users/${parsedRealUserId}/profile/`; 
        
        try { 
            const response = await fetch(apiUrl, { 
                method: 'GET', 
                headers: { 
                    'Authorization': `Token ${authToken}`, 
                    'Content-Type': 'application/json' 
                } 
            }); 
            
            if (response.ok) { 
                const data = await response.json(); 
                setRealUserProfileData(data); 
                console.log("Real user profile fetched:", data); 
            } else { 
                let errorMsg = 'Failed to load real user profile.'; 
                try { 
                    const errorData = await response.json(); 
                    errorMsg = errorData.detail || `Error ${response.status}`; 
                } catch(e) { 
                    errorMsg = `Error ${response.status}`; 
                } 
                setRealProfileError(errorMsg); 
            } 
        } catch (err) { 
            console.error("Network error fetching real user profile:", err); 
            setRealProfileError("Network error fetching profile."); 
        } finally { 
            setProfileLoading(false); 
        }
    }, [authToken, realUserId]);
    const fetchFakeUserProfile = useCallback(async () => {
        const parsedFakeUserId = parseInt(fakeUserId, 10); 
        if (!authToken || isNaN(parsedFakeUserId)) { 
            setFakeProfileError("Cannot fetch profile: Invalid Fake User ID or Auth token missing."); 
            return; 
        } 
        console.log(`Fetching profile data for fake user ${parsedFakeUserId}...`); 
        setFakeProfileLoading(true); 
        setFakeProfileError(null); 
        
        // Korrigierte URL für Profile
        const apiUrl = `http://127.0.0.1:8000/api/accounts/users/${parsedFakeUserId}/profile/`; 
        
        try { 
            const response = await fetch(apiUrl, { 
                method: 'GET', 
                headers: { 
                    'Authorization': `Token ${authToken}`, 
                    'Content-Type': 'application/json' 
                } 
            }); 
            
            if (response.ok) { 
                const data = await response.json(); 
                setFakeUserProfileData(data); 
                console.log("Fake user profile fetched:", data); 
            } else { 
                let errorMsg = 'Failed to load fake user profile.'; 
                try { 
                    const errorData = await response.json(); 
                    errorMsg = errorData.detail || `Error ${response.status}`; 
                } catch(e) { 
                    errorMsg = `Error ${response.status}`; 
                } 
                setFakeProfileError(errorMsg); 
            } 
        } catch (err) { 
            console.error("Network error fetching fake user profile:", err); 
            setFakeProfileError("Network error fetching fake profile."); 
        } finally { 
            setFakeProfileLoading(false); 
        }
    }, [authToken, fakeUserId]);
    const handleSendMessage = async (event) => {
         event.preventDefault(); const contentToSend = newMessage.trim(); if (!contentToSend) { setError("Cannot send an empty message."); return; } if (!authToken) { setError("Authentication error. Please log in again."); return; } console.log(`Moderator attempting to send reply as Fake User ${fakeUserId} to Real User ${realUserId}`); setError(null); setSuggestionError(null); const apiUrl = 'http://127.0.0.1:8000/api/messaging/secure/response/'; const payload = { fake_user_id: parseInt(fakeUserId, 10), real_user_id: parseInt(realUserId, 10), content: contentToSend }; try { const response = await fetch(apiUrl, { method: 'POST', headers: { 'Authorization': `Token ${authToken}`, 'Content-Type': 'application/json', }, body: JSON.stringify(payload) }); if (response.ok) { console.log("Moderator reply sent successfully via API."); setNewMessage(''); fetchMessages(); } else { let errorMsg = 'Failed to send reply.'; try { const errorData = await response.json(); console.error('Send reply failed (Backend Response):', errorData); if (typeof errorData === 'object' && errorData !== null) { errorMsg = errorData.detail || errorData.error || Object.values(errorData).flat()[0] || `Server error ${response.status}`; } else { errorMsg = `Error ${response.status}`; } } catch (e) { errorMsg = `Error: ${response.status} ${response.statusText}`; } setError(errorMsg); } } catch(error) { console.error("Network error sending reply:", error); setError('Network error while sending reply. Please try again.'); }
     };
    const handleSaveNotes = useCallback(async () => {
         const parsedRealUserId = parseInt(realUserId, 10); 
         if (!authToken || isNaN(parsedRealUserId)) { 
             setNotesError("Cannot save notes: Invalid Real User ID or Auth token missing."); 
             return; 
         } 
         console.log(`ModeratorChatPage: Saving notes for user ${parsedRealUserId}...`); 
         setNotesLoading(true); 
         setNotesError(null); 
         setNotesSaveSuccess(false); 
         
         try { 
             // Korrigierte URL für Notizen
             const apiUrl = `http://127.0.0.1:8000/api/accounts/users/${parsedRealUserId}/notes/`; 
             const payload = { moderator_notes: moderatorNotes }; 
             const response = await fetch(apiUrl, { 
                 method: 'PATCH', 
                 headers: { 
                     'Authorization': `Token ${authToken}`, 
                     'Content-Type': 'application/json', 
                 }, 
                 body: JSON.stringify(payload) 
             }); 
             
             if (response.ok) { 
                 const data = await response.json(); 
                 console.log(`Notes saved successfully for user ${parsedRealUserId}.`); 
                 setNotesSaveSuccess(true); 
                 setTimeout(() => setNotesSaveSuccess(false), 3000); 
             } else { 
                 let errorMsg = 'Failed to save notes.'; 
                 try { 
                     const errorData = await response.json(); 
                     console.error('Error saving notes (Backend Response):', errorData); 
                     errorMsg = errorData.detail || (errorData.moderator_notes ? `Notes: ${errorData.moderator_notes[0]}` : `Error ${response.status}`); 
                 } catch (e) { 
                     errorMsg = `Error: ${response.status} ${response.statusText}`; 
                 } 
                 setNotesError(errorMsg); 
             } 
         } catch (err) { 
             console.error("Network error saving notes:", err); 
             setNotesError("Network error saving notes. Please try again."); 
         } finally { 
             setNotesLoading(false); 
         }
    }, [authToken, realUserId, moderatorNotes]);
    const handleGetSuggestion = useCallback(async () => {
        const parsedRealUserId = parseInt(realUserId, 10);
        const parsedFakeUserId = parseInt(fakeUserId, 10);
        
        if (!authToken || isNaN(parsedRealUserId) || isNaN(parsedFakeUserId)) {
            setSuggestionError("Cannot get suggestion: Invalid User IDs or Auth token missing.");
            return;
        }
        
        console.log(`Attempting to get enhanced AI suggestions for ${parsedRealUserId} <-> ${parsedFakeUserId}`);
        setIsSuggesting(true);
        setSuggestionError(null);
        setAiSuggestions([]);
        
        const apiUrl = 'http://127.0.0.1:8000/api/messaging/advanced-reply-options/';
        const payload = {
            real_user_id: parsedRealUserId,
            fake_user_id: parsedFakeUserId,
            num_suggestions: 4  // Anzahl der gewünschten Vorschläge
        };
        
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log("Enhanced AI suggestions received:", data.suggestions);
                setAiSuggestions(data.suggestions);
                
                // Wenn mindestens ein Vorschlag vorhanden ist, setzen wir den ersten als Standard
                if (data.suggestions && data.suggestions.length > 0) {
                    setNewMessage(data.suggestions[0].content);
                }
            } else {
                let errorMsg = 'Failed to get AI suggestions.';
                try {
                    const errorData = await response.json();
                    console.error('Error getting AI suggestions (Backend Response):', errorData);
                    if (response.status === 403) {
                        errorMsg = errorData.detail || "Permission denied or AI assist not enabled for this conversation.";
                    } else {
                        errorMsg = errorData.detail || `Error ${response.status}`;
                    }
                } catch (e) {
                    errorMsg = `Error: ${response.status} ${response.statusText}`;
                }
                setSuggestionError(errorMsg);
            }
        } catch (err) {
            console.error("Network error getting AI suggestions:", err);
            setSuggestionError("Network error getting AI suggestions.");
        } finally {
            setIsSuggesting(false);
        }
    }, [authToken, realUserId, fakeUserId, setNewMessage]);
    
    // Funktion zum Auswählen und Senden eines Vorschlags
    const handleSelectSuggestion = useCallback(async (content, event) => {
        // Verhindere Standardverhalten, falls ein Event übergeben wurde
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        // Sende den Vorschlag direkt, ohne ihn ins Eingabefeld zu setzen
        if (!content.trim()) {
            setError("Cannot send an empty message.");
            return;
        }
        
        if (!authToken) {
            setError("Authentication error. Please log in again.");
            return;
        }
        
        console.log(`Moderator sending AI suggestion as Fake User ${fakeUserId} to Real User ${realUserId}`);
        setError(null);
        setSuggestionError(null);
        
        const apiUrl = 'http://127.0.0.1:8000/api/messaging/secure/response/';
        const payload = {
            fake_user_id: parseInt(fakeUserId, 10),
            real_user_id: parseInt(realUserId, 10),
            content: content
        };
        
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                console.log("AI suggestion sent successfully via API.");
                setNewMessage('');
                setAiSuggestions([]); // Schließe die Vorschläge nach dem Senden
                fetchMessages();
            } else {
                let errorMsg = 'Failed to send reply.';
                try {
                    const errorData = await response.json();
                    console.error('Send reply failed (Backend Response):', errorData);
                    if (typeof errorData === 'object' && errorData !== null) {
                        errorMsg = errorData.detail || errorData.error || Object.values(errorData).flat()[0] || `Server error ${response.status}`;
                    } else {
                        errorMsg = `Error ${response.status}`;
                    }
                } catch (e) {
                    errorMsg = `Error: ${response.status} ${response.statusText}`;
                }
                setError(errorMsg);
            }
        } catch(error) {
            console.error("Network error sending reply:", error);
            setError('Network error while sending reply. Please try again.');
        }
    }, [authToken, realUserId, fakeUserId, fetchMessages]);

    // Funktion zum Abrufen unbeantworteter Gespräche
    const fetchUnansweredConversations = useCallback(async () => {
        if (!authToken) {
            setUnansweredError("Cannot fetch unanswered conversations: Auth token missing.");
            return;
        }
        
        console.log("Fetching unanswered conversations...");
        setUnansweredLoading(true);
        setUnansweredError(null);
        
        try {
            const apiUrl = 'http://127.0.0.1:8000/api/messaging/secure/managed-chats/?unanswered=true';
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log("Unanswered conversations fetched:", data);
                setUnansweredConversations(data);
            } else {
                let errorMsg = 'Failed to load unanswered conversations.';
                try {
                    const errorData = await response.json();
                    console.error('Error fetching unanswered conversations (Backend Response):', errorData);
                    errorMsg = errorData.detail || errorData.error || `Error ${response.status}`;
                } catch (e) {
                    errorMsg = `Error: ${response.status} ${response.statusText}`;
                }
                setUnansweredError(errorMsg);
            }
        } catch (err) {
            console.error("Network error fetching unanswered conversations:", err);
            setUnansweredError("Network error. Please try again.");
        } finally {
            setUnansweredLoading(false);
        }
    }, [authToken]);
    
    // Funktion zum Navigieren zu einem anderen Gespräch
    const navigateToConversation = useCallback((realUserId, fakeUserId) => {
        navigate(`/moderator/chat/${realUserId}/${fakeUserId}`);
    }, [navigate]);

    // useEffect ruft jetzt alle Fetch-Funktionen auf
    useEffect(() => {
        if (authToken && user && realUserId && fakeUserId) {
            fetchMessages(); 
            fetchNotes(); 
            fetchConversationAiMode(); 
            fetchRealUserProfile(); 
            fetchFakeUserProfile();
            fetchUnansweredConversations();
        }
    }, [authToken, user, realUserId, fakeUserId, fetchMessages, fetchNotes, fetchConversationAiMode, fetchRealUserProfile, fetchFakeUserProfile, fetchUnansweredConversations]);


    // JSX Rendering
    const initialDataLoading = isLoading || modeLoading || profileLoading || fakeProfileLoading;

    if (initialDataLoading && !realUserProfileData && !fakeUserProfileData) {
        return <div className={styles.loadingMessage}>Chat & Profildaten werden geladen...</div>;
    }
    
    if (error && messages.length === 0) {
        return <div className={styles.errorMessage}>Fehler beim Laden des Chats: {error}</div>;
    }

    // Bedingung für AI Button Anzeige
    const showAiButton = conversationAiMode === 'ASSISTED' && !!user?.can_use_ai_assist;

    // Location Strings für beide Profile bauen
    let realUserLocationString = '-'; 
    if (realUserProfileData) { 
        const parts = [
            realUserProfileData.city, 
            realUserProfileData.state, 
            realUserProfileData.postal_code, 
            realUserProfileData.country
        ].filter(Boolean); 
        realUserLocationString = parts.join(', ') || '-'; 
    }
    
    let fakeUserLocationString = '-'; 
    if (fakeUserProfileData) { 
        const parts = [
            fakeUserProfileData.city, 
            fakeUserProfileData.state, 
            fakeUserProfileData.postal_code, 
            fakeUserProfileData.country
        ].filter(Boolean); 
        fakeUserLocationString = parts.join(', ') || '-'; 
    }

    return (
        <div>
            <div className={styles.header}>
                {/* Fehlermeldungen */}
                {error && <div className={styles.errorMessage}>Chat-Fehler: {error}</div>}
                {notesError && <div className={styles.errorMessage}>Notizen-Fehler: {notesError}</div>}
                {suggestionError && <div className={styles.errorMessage}>KI-Vorschlag-Fehler: {suggestionError}</div>}
                {modeError && <div className={styles.errorMessage}>KI-Modus-Fehler: {modeError}</div>}
                {realProfileError && <div className={styles.errorMessage}>Fehler beim echten Profil: {realProfileError}</div>}
                {fakeProfileError && <div className={styles.errorMessage}>Fehler beim Fake-Profil: {fakeProfileError}</div>}
                {notesSaveSuccess && <div className={styles.successMessage}>Notizen erfolgreich gespeichert!</div>}
                {unansweredError && <div className={styles.errorMessage}>Fehler beim Laden unbeantworteter Gespräche: {unansweredError}</div>}
            </div>
            
            {/* Leiste mit unbeantworteten Gesprächen */}
            <div className={styles.unansweredConversationsBar}>
                {unansweredLoading ? (
                    <div className={styles.noUnansweredMessage}>Lade unbeantwortete Gespräche...</div>
                ) : unansweredConversations.length === 0 ? (
                    <div className={styles.noUnansweredMessage}>Keine unbeantworteten Gespräche</div>
                ) : (
                    <>
                        {unansweredConversations.map(convo => (
                            <div 
                                key={`${convo.real_user.id}-${convo.fake_user.id}`} 
                                className={`${styles.conversationChip} ${
                                    parseInt(realUserId, 10) === convo.real_user.id && 
                                    parseInt(fakeUserId, 10) === convo.fake_user.id ? 
                                    styles.active : ''
                                }`}
                                onClick={() => navigateToConversation(convo.real_user.id, convo.fake_user.id)}
                            >
                                <FiMessageSquare style={{ marginRight: '0.5rem' }} />
                                {convo.real_user.username} → {convo.fake_user.username}
                            </div>
                        ))}
                    </>
                )}
            </div>

            <div className={styles.outerContainer}>
                {/* Linke Seite - Echter Benutzer */}
                <div className={`${styles.sidePanel} ${styles.realUserPanel}`}>
                    {/* Profilbild */}
                    <div className={styles.profileContainer}>
                        {!profileLoading && realUserProfileData && realUserProfileData.profile_picture_url ? (
                            <img 
                                src={realUserProfileData.profile_picture_url} 
                                alt={`${realUserProfileData?.username || 'User'}'s profile`} 
                                className={styles.profileImage}
                            />
                        ) : (
                            <div className={styles.profilePlaceholder}>No Pic</div>
                        )}
                    </div>
                    
                    {/* Benutzerinfo */}
                    <div className={styles.userInfoPanel}>
                        <h3>{realUserName}</h3>
                        {profileLoading ? (
                            <p>Profil wird geladen...</p>
                        ) : (
                            realUserProfileData ? (
                                <div className={styles.userDetailsList}>
                                    {/* Coin-Balance Anzeige - Hervorgehoben */}
                                    <div className={`${styles.userDetailItem} ${styles.coinBalanceItem}`}>
                                        <span className={styles.detailLabel}>Coins:</span>
                                        <span className={styles.detailValue}>
                                            <strong>{realUserProfileData.coin_balance || 0}</strong>
                                        </span>
                                    </div>
                                    <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Geburtsdatum:</span>
                                        <span className={styles.detailValue}>{realUserProfileData.birth_date || '-'}</span>
                                    </div>
                                    <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Standort:</span>
                                        <span className={styles.detailValue}>{realUserLocationString}</span>
                                    </div>
                                    {realUserProfileData.gender && (
                                        <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Geschlecht:</span>
                                            <span className={styles.detailValue}>
                                                {realUserProfileData.gender === 'MALE' ? 'Männlich' : 
                                                realUserProfileData.gender === 'FEMALE' ? 'Weiblich' : 
                                                realUserProfileData.gender}
                                            </span>
                                        </div>
                                    )}
                                    {realUserProfileData.seeking && (
                                        <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Sucht:</span>
                                            <span className={styles.detailValue}>
                                                {realUserProfileData.seeking === 'MALE' ? 'Männer' : 
                                                realUserProfileData.seeking === 'FEMALE' ? 'Frauen' : 
                                                realUserProfileData.seeking}
                                            </span>
                                        </div>
                                    )}
                                    {realUserProfileData.about_me && (
                                        <div className={styles.aboutMePanel}>
                                            <h4>Über mich</h4>
                                            <p>{realUserProfileData.about_me}</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p>Profildaten konnten nicht geladen werden</p>
                            )
                        )}
                    </div>
                </div>
                
                {/* Chat-Container in der Mitte */}
                <div className={styles.chatContainer}>
                    {/* Zurück-Button über der Nachrichtenliste */}
                    <div className={styles.backButtonContainer}>
                        <Link to="/moderator/dashboard" className={styles.backButton}>
                            <FiArrowLeft size={20} />
                            <span>Zurück zum Dashboard</span>
                        </Link>
                    </div>
                    
                    {/* Nachrichtenliste */}
                    <div className={styles.messageList} ref={messageListRef}>
                        {isLoading && messages.length === 0 && (
                            <p className={styles.loadingMessage}>Nachrichten werden geladen...</p>
                        )}
                        {!isLoading && messages.length === 0 ? (
                            <p className={styles.infoMessage}>Noch keine Nachrichten in diesem Gespräch.</p>
                        ) : (
                            messages.map(message => {
                                const isRealUserMessage = message.sender.id === parseInt(realUserId, 10);
                                const messageClass = isRealUserMessage ? styles.realUserMessage : styles.fakeUserMessage;
                                
                                return (
                                    <div key={message.id} className={`${styles.messageItem} ${messageClass}`}>
                                        <div className={styles.messageContent}>{message.content}</div>
                                        <div className={styles.messageTimestamp}>
                                            {new Date(message.timestamp).toLocaleString()}
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                    
                    {/* Eingabeformular */}
                    <form onSubmit={handleSendMessage} className={styles.inputForm}>
                        <input 
                            type="text" 
                            value={newMessage} 
                            onChange={(e) => setNewMessage(e.target.value)} 
                            placeholder={`Als ${fakeUserName} antworten...`} 
                            className={styles.messageInput}
                            required 
                        />
                        {!modeLoading && showAiButton && (
                            <button 
                                type="button" 
                                onClick={handleGetSuggestion} 
                                disabled={isSuggesting} 
                                className={styles.aiButton}
                            >
                                <FiCpu style={{ marginRight: '0.5rem' }} />
                                {isSuggesting ? 'Wird geladen...' : 'KI-Vorschläge'}
                            </button>
                        )}
                        
                        {/* Anzeige der KI-Vorschläge */}
                        {aiSuggestions.length > 0 && (
                            <div className={styles.aiSuggestionsContainer}>
                                <h3 className={styles.aiSuggestionsTitle}>KI-Vorschläge:</h3>
                                <div className={styles.aiSuggestionsList}>
                                    {aiSuggestions.map((suggestion, index) => (
                                        <div key={index} className={styles.aiSuggestionCard}>
                                            <div className={styles.aiSuggestionHeader}>
                                                <strong>{suggestion.description}</strong>
                                            </div>
                                            <div className={styles.aiSuggestionContent}>
                                                {suggestion.content}
                                            </div>
                                            <button 
                                                onClick={(e) => handleSelectSuggestion(suggestion.content, e)}
                                                className={styles.aiSuggestionSelectButton}
                                            >
                                                Diesen Vorschlag senden!
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        {/* Senden-Button nur anzeigen, wenn keine KI-Vorschläge angezeigt werden */}
                        {aiSuggestions.length === 0 && (
                            <button type="submit" className={styles.sendButton}>
                                <FiSend style={{ marginRight: '0.5rem' }} />
                                Senden
                            </button>
                        )}
                    </form>
                </div>
                
                {/* Rechte Seite - Fake Benutzer */}
                <div className={`${styles.sidePanel} ${styles.fakeUserPanel}`}>
                    {/* Profilbild */}
                    <div className={styles.profileContainer}>
                        {!fakeProfileLoading && fakeUserProfileData && fakeUserProfileData.profile_picture_url ? (
                            <img 
                                src={fakeUserProfileData.profile_picture_url} 
                                alt={`${fakeUserProfileData?.username || 'User'}'s profile`} 
                                className={styles.profileImage}
                            />
                        ) : (
                            <div className={styles.profilePlaceholder}>No Pic</div>
                        )}
                    </div>
                    
                    {/* Benutzerinfo */}
                    <div className={styles.userInfoPanel}>
                        <h3>{fakeUserName}</h3>
                        {fakeProfileLoading ? (
                            <p>Profil wird geladen...</p>
                        ) : (
                            fakeUserProfileData ? (
                                <div className={styles.userDetailsList}>
                                    <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Geburtsdatum:</span>
                                        <span className={styles.detailValue}>{fakeUserProfileData.birth_date || '-'}</span>
                                    </div>
                                    <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Standort:</span>
                                        <span className={styles.detailValue}>{fakeUserLocationString}</span>
                                    </div>
                                    {fakeUserProfileData.gender && (
                                        <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Geschlecht:</span>
                                            <span className={styles.detailValue}>
                                                {fakeUserProfileData.gender === 'MALE' ? 'Männlich' : 
                                                fakeUserProfileData.gender === 'FEMALE' ? 'Weiblich' : 
                                                fakeUserProfileData.gender}
                                            </span>
                                        </div>
                                    )}
                                    {fakeUserProfileData.seeking && (
                                        <div className={styles.userDetailItem}>
                                        <span className={styles.detailLabel}>Sucht:</span>
                                            <span className={styles.detailValue}>
                                                {fakeUserProfileData.seeking === 'MALE' ? 'Männer' : 
                                                fakeUserProfileData.seeking === 'FEMALE' ? 'Frauen' : 
                                                fakeUserProfileData.seeking}
                                            </span>
                                        </div>
                                    )}
                                    {fakeUserProfileData.about_me && (
                                        <div className={styles.aboutMePanel}>
                                            <h4>Über mich</h4>
                                            <p>{fakeUserProfileData.about_me}</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p>Profildaten konnten nicht geladen werden</p>
                            )
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
export default ModeratorChatPage;
