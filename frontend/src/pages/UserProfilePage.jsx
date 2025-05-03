// frontend/src/pages/UserProfilePage.jsx (Mit Like-Button)
import React, { useState, useEffect, useContext, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './UserProfilePage.module.css';
import FsLightbox from "fslightbox-react"; // FsLightbox importiert

// Hilfsfunktion zur Altersberechnung
function calculateAge(birthDateString) { /* ... */ }

function UserProfilePage() {
    const { userId } = useParams();
    const { authToken, user: loggedInUser } = useContext(AuthContext);
    const navigate = useNavigate();

    const [profileData, setProfileData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isLiked, setIsLiked] = useState(false);
    const [isLikeLoading, setIsLikeLoading] = useState(false);

    // States für FsLightbox
    const [lightboxToggler, setLightboxToggler] = useState(false);
    const [lightboxImageIndex, setLightboxImageIndex] = useState(0);


    // Funktion zum Abrufen der Profildaten (MIT LOGGING)
    const fetchProfileData = useCallback(async () => {
        if (!authToken || !userId) { setError("Profil kann nicht geladen werden: Auth Token oder Benutzer-ID fehlt."); setIsLoading(false); return; }
        console.log(`[fetchProfileData] Starting fetch for user ${userId}...`); // LOG 1
        setIsLoading(true); setError(null); const apiUrl = `http://127.0.0.1:8000/api/accounts/users/${userId}/profile/`;
        try {
            console.log(`[fetchProfileData] Before fetch call to ${apiUrl}`); // LOG 2
            const response = await fetch(apiUrl, { method: 'GET', headers: { 'Authorization': `Token ${authToken}`, 'Content-Type': 'application/json', } });
            console.log(`[fetchProfileData] After fetch call. Status: ${response.status}`); // LOG 3
            if (response.ok) {
                console.log("[fetchProfileData] Response OK. Before response.json()"); // LOG 4
                const data = await response.json();
                console.log("[fetchProfileData] After response.json(). Data:", data); // LOG 5
                setProfileData(data);
                setIsLiked(data.is_liked || false);
                console.log("[fetchProfileData] After setProfileData(data)"); // LOG 6
            } else {
                let errorMsg = 'Profil konnte nicht geladen werden.'; if (response.status === 404) { errorMsg = "Benutzerprofil nicht gefunden."; } else { try { const errorData = await response.json(); errorMsg = errorData.detail || `Fehler ${response.status}`; } catch (e) { errorMsg = `Fehler: ${response.status} ${response.statusText}`; } } console.error('[fetchProfileData] Error response from backend:', errorMsg); setError(errorMsg);
            }
        } catch (err) { console.error("[fetchProfileData] Network or processing error:", err); setError("Netzwerkfehler oder Verarbeitungsfehler beim Laden der Profildaten."); }
        finally { console.log("[fetchProfileData] Entering finally block. Setting isLoading to false."); setIsLoading(false); } // LOG 7
    }, [authToken, userId]);

    // useEffect zum Laden der Daten
    useEffect(() => { if (authToken && userId) { fetchProfileData(); } }, [authToken, userId, fetchProfileData]);

    // Handler für "Nachricht schreiben" Button
    const handleStartChat = useCallback(() => { navigate(`/chat/${userId}`); }, [navigate, userId]);

    // Handler für Like/Unlike Button
    const handleLikeToggle = useCallback(async () => {
        if (!authToken || !userId || isLikeLoading) return;
        
        setIsLikeLoading(true);
        const apiUrl = `http://127.0.0.1:8000/api/accounts/users/${userId}/like/`;
        
        try {
            const method = isLiked ? 'DELETE' : 'POST';
            const response = await fetch(apiUrl, {
                method,
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                setIsLiked(!isLiked);
                // Optional: Erfolgsmeldung anzeigen
            } else {
                // Fehlerbehandlung
                const errorData = await response.json();
                console.error('Fehler beim Like/Unlike:', errorData);
                // Optional: Fehlermeldung anzeigen
            }
        } catch (err) {
            console.error('Netzwerkfehler beim Like/Unlike:', err);
            // Optional: Fehlermeldung anzeigen
        } finally {
            setIsLikeLoading(false);
        }
    }, [authToken, userId, isLiked, isLikeLoading]);

    // Lade- und Fehlerzustände
    if (isLoading) { return <div className={styles.loadingMessage}>Lade Profil...</div>; }
    if (error) { return <div className={styles.errorMessage}>Fehler beim Laden des Profils: {error}</div>; }
    if (!profileData) { return <div className={styles.infoMessage}>Keine Profildaten verfügbar.</div>; }

    // Location String bauen
    const locationParts = [ profileData.city, profileData.state ].filter(Boolean);
    const locationString = locationParts.join(', ') || '-';
    // Alter berechnen
    const age = calculateAge(profileData.birth_date);
    // URL für das Haupt-Profilbild bestimmen
    const mainImageUrl = profileData.profile_picture_url || (profileData.image_gallery && profileData.image_gallery.length > 0 ? profileData.image_gallery[0] : null);
    // Daten für Lightbox vorbereiten
    const gallerySources = profileData.image_gallery || [];

    // --- Finale JSX-Anzeige ---
    return (
        <>
            <div className={styles.profileContainer}>
                <h1 className={styles.profileHeader}> Profil von {profileData.username} </h1>

                {/* --- Zurück-Link WIEDER HINZUGEFÜGT --- */}
                <div className={styles.backLinkContainer}>
                    <Link to="/userdashboard" className={styles.backLink}>
                        &larr; Zurück zum Dashboard
                    </Link>
                </div>
                {/* --- ENDE --- */}

                {/* Hauptbereich */}
                <div className={styles.profileDetailsSection}> 
                    <div className={styles.detailsSection}> 
                        <div className={styles.detailsTextColumn}> 
                            <strong>Details:</strong> 
                            <ul className={styles.detailsList}> 
                                <li>Alter: {age !== null ? age : '-'}</li> 
                                <li>Stadt: {profileData.city || '-'}</li> 
                                <li>Bundesland: {profileData.state || '-'}</li> 
                            </ul> 
                        </div> 
                        {mainImageUrl && ( 
                            <div className={styles.profileImageColumn}> 
                                <img src={mainImageUrl} alt={`Profilbild von ${profileData.username}`} className={styles.profileDetailImage} /> 
                            </div> 
                        )} 
                    </div> 
                    <div className={styles.aboutSection}> 
                        <strong>Über mich:</strong> 
                        <p className={styles.aboutText}> 
                            {profileData.about_me || '-'} 
                        </p> 
                    </div> 
                </div>

                {/* Chat-Button, Like-Button & Bildergalerie */}
                <div className={styles.imageGalleryContainer}>
                    {loggedInUser?.pk !== profileData.pk && (
                        <div className={styles.actionButtonsContainer}>
                            <button onClick={handleStartChat} className={styles.sendMessageButton}>
                                Nachricht schreiben
                            </button>
                            <button 
                                onClick={handleLikeToggle} 
                                className={`${styles.likeButton} ${isLiked ? styles.liked : ''}`}
                                disabled={isLikeLoading}
                            >
                                {isLikeLoading ? 'Wird bearbeitet...' : isLiked ? '❤️ Favorit' : '🤍 Favorit hinzufügen'}
                            </button>
                        </div>
                    )}
                    {gallerySources.length > 0 ? ( 
                        <> 
                            <div className={styles.imageGrid}> 
                                {gallerySources.map((imageUrl, index) => ( 
                                    <div 
                                        key={index} 
                                        className={styles.galleryImageWrapper} 
                                        onClick={() => { 
                                            setLightboxImageIndex(index); 
                                            setLightboxToggler(!lightboxToggler); 
                                        }} 
                                        style={{ cursor: 'pointer' }} 
                                    > 
                                        <img 
                                            src={imageUrl} 
                                            alt={`Profilbild ${index + 1} von ${profileData.username}`} 
                                            className={styles.galleryImage} 
                                        /> 
                                    </div> 
                                ))} 
                            </div> 
                        </> 
                    ) : ( 
                        !mainImageUrl && <p className={styles.infoMessage}>Keine Bilder vorhanden.</p> 
                    )}
                </div>

                {/* Link zu Settings */}
                {loggedInUser?.pk === profileData.pk && ( 
                    <div className={styles.editLinkContainer}> 
                        <Link to="/profile-settings">Dein Profil & Bilder bearbeiten</Link> 
                    </div> 
                )}
            </div>

            {/* FsLightbox Komponente */}
            <FsLightbox toggler={lightboxToggler} sources={gallerySources} sourceIndex={lightboxImageIndex} />
        </>
    );
}

export default UserProfilePage;
