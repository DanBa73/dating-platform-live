// frontend/src/pages/ProfileSettingsPage.jsx (Reduzierte vertikale Abstände)
import React, { useState, useEffect, useContext, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext.jsx';
import styles from './FormPages.module.css';
import { useNavigate } from 'react-router-dom';

const countryStateData = {
    DE: ['Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen'],
    AT: ['Burgenland', 'Kärnten', 'Niederösterreich', 'Oberösterreich', 'Salzburg', 'Steiermark', 'Tirol', 'Vorarlberg', 'Wien'],
    CH: ['Aargau', 'Appenzell Ausserrhoden', 'Appenzell Innerrhoden', 'Basel-Landschaft', 'Basel-Stadt', 'Bern', 'Freiburg', 'Genf', 'Glarus', 'Graubünden', 'Jura', 'Luzern', 'Neuenburg', 'Nidwalden', 'Obwalden', 'Schaffhausen', 'Schwyz', 'Solothurn', 'St. Gallen', 'Tessin', 'Thurgau', 'Uri', 'Waadt', 'Wallis', 'Zug', 'Zürich']
};

function ProfileSettingsPage() {
  const { authToken, user, refreshAuthUser } = useContext(AuthContext);
  const navigate = useNavigate();

  // --- States ---
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [profileImages, setProfileImages] = useState([]);
  const [imagesLoading, setImagesLoading] = useState(false);
  const [imagesError, setImagesError] = useState(null);
  const [deletingImageId, setDeletingImageId] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  const [birthDate, setBirthDate] = useState('');
  const [country, setCountry] = useState('');
  const [stateName, setStateName] = useState('');
  const [city, setCity] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [aboutMe, setAboutMe] = useState('');
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileSaveError, setProfileSaveError] = useState(null);
  const [profileSaveSuccess, setProfileSaveSuccess] = useState(false);
  const [stateOptions, setStateOptions] = useState([]);
  // --- Ende States ---

  // --- useEffects & Callbacks ---
  useEffect(() => { if (user) { setBirthDate(user.birth_date || ''); setCountry(user.country || ''); setStateName(user.state || ''); setCity(user.city || ''); setPostalCode(user.postal_code || ''); setAboutMe(user.about_me || ''); }}, [user]);
  useEffect(() => { if (country && countryStateData[country]) { setStateOptions(countryStateData[country]); } else { setStateOptions([]); } }, [country]);

  const fetchProfileImages = useCallback(async () => { if (!user || !authToken) return; setImagesLoading(true); setImagesError(null); setDeleteError(null); try { const response = await fetch(`http://127.0.0.1:8000/api/users/${user.pk}/profile-images/`, { headers: { 'Authorization': `Token ${authToken}` } }); if (!response.ok) { let errorMsg = `Fehler beim Laden der Bilder (Status: ${response.status})`; try { const errorData = await response.json(); errorMsg = errorData.detail || JSON.stringify(errorData); } catch (e) { /* ignore */ } throw new Error(`Fehler beim Laden der Bilder: ${errorMsg}`); } const data = await response.json(); setProfileImages(data); } catch (error) { console.error("Error fetching images:", error); setImagesError(error.message || 'Bilder konnten nicht geladen werden.'); } finally { setImagesLoading(false); } }, [authToken, user]);
  useEffect(() => { fetchProfileImages(); }, [fetchProfileImages]);

  const handleFileChange = (event) => { if (event.target.files && event.target.files[0]) { setSelectedFile(event.target.files[0]); setUploadError(null); setUploadSuccess(false); } else { setSelectedFile(null); } };
  const handleUploadSubmit = useCallback(async (event) => { event.preventDefault(); if (!selectedFile || !authToken) return; setIsUploading(true); setUploadError(null); setUploadSuccess(false); const formData = new FormData(); formData.append('image', selectedFile); try { const response = await fetch('http://127.0.0.1:8000/api/profile-images/', { method: 'POST', headers: { 'Authorization': `Token ${authToken}` }, body: formData, }); if (response.ok) { setUploadSuccess(true); setSelectedFile(null); const fileInput = document.getElementById('imageUpload'); if(fileInput) fileInput.value = ''; fetchProfileImages(); setTimeout(() => setUploadSuccess(false), 3000); } else { let errorMessage = `Upload fehlgeschlagen (Status: ${response.status})`; try { const errorData = await response.json(); errorMessage = errorData.detail || errorData.image || JSON.stringify(errorData); } catch (e) { /* ignore */ } setUploadError(`Upload fehlgeschlagen: ${errorMessage}`); } } catch (error) { console.error("Network or upload error:", error); setUploadError('Upload wegen Netzwerk- oder Serverproblem fehlgeschlagen.'); } finally { setIsUploading(false); } }, [authToken, selectedFile, fetchProfileImages]);
  const handleDeleteImage = useCallback(async (imageId) => { if (!authToken) return; setDeletingImageId(imageId); setDeleteError(null); try { const response = await fetch(`http://127.0.0.1:8000/api/profile-images/${imageId}/`, { method: 'DELETE', headers: { 'Authorization': `Token ${authToken}` }, }); if (response.ok || response.status === 204) { fetchProfileImages(); } else { let errorMessage = `Löschen fehlgeschlagen (Status: ${response.status})`; try { const errorData = await response.json(); errorMessage = errorData.detail || JSON.stringify(errorData); } catch (e) { /* ignore */ } setDeleteError(`Löschen fehlgeschlagen: ${errorMessage}`); } } catch (error) { console.error("Network or delete error:", error); setDeleteError('Löschen wegen Netzwerk- oder Serverproblem fehlgeschlagen.'); } finally { setDeletingImageId(null); } }, [authToken, fetchProfileImages]);
  const handleProfileSubmit = async (event) => { event.preventDefault(); setProfileSaveError(null); setProfileSaveSuccess(false); setIsSavingProfile(true); const api = 'http://127.0.0.1:8000/api/auth/user/'; const data = { birth_date: birthDate || null, country: country || null, state: stateName || null, city: city || null, postal_code: postalCode || null, about_me: aboutMe || null, }; try { const response = await fetch(api, { method: 'PATCH', headers: { 'Authorization': `Token ${authToken}`, 'Content-Type': 'application/json', }, body: JSON.stringify(data), }); if (response.ok) { setProfileSaveSuccess(true); setTimeout(() => setProfileSaveSuccess(false), 3000); if (refreshAuthUser) { await refreshAuthUser(); } } else { let errorMessage = `Profil speichern fehlgeschlagen (Status: ${response.status})`; try { const errorData = await response.json(); errorMessage = Object.entries(errorData).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`).join('; ') || `Error ${response.status}`; } catch (e) { /* ignore */ } setProfileSaveError(`Profil speichern fehlgeschlagen: ${errorMessage}`); } } catch (err) { console.error("Network error during profile save:", err); setProfileSaveError("Netzwerkfehler. Bitte Verbindung prüfen."); } finally { setIsSavingProfile(false); } };
  const handleCountryChange = (event) => { const newCountry = event.target.value; setCountry(newCountry); setStateName(''); };
  // --- Ende useEffects & Callbacks ---

  return (
      <div className={styles.formContainerWide}>

          {/* Formular für Profildaten */}
          {/* *** GEÄNDERT: Abstände reduziert *** */}
          <form onSubmit={handleProfileSubmit} style={{ marginBottom: '1.5rem', borderTop: '1px solid #eee', paddingTop: '1.5rem' }}>
              <h3 className={styles.formTitle} style={{ fontSize: '1.5em', marginTop: 0 }}>Deine Angaben</h3>
              {profileSaveError && <p className={styles.error}>{profileSaveError}</p>}
              {profileSaveSuccess && <p style={{ color: 'green', textAlign: 'center', marginBottom: '15px' }}>Profil erfolgreich aktualisiert!</p>}
              {/* ... Formularfelder ... */}
              <div className={styles.formGroup}> <label htmlFor="birthDate">Geburtsdatum:</label> <input type="date" id="birthDate" value={birthDate} onChange={(e) => setBirthDate(e.target.value)} /> </div>
              <div className={styles.formRow}> <div className={styles.formGroup}> <label htmlFor="country">Land:</label> <select id="country" value={country} onChange={handleCountryChange} > <option value="">Bitte auswählen...</option> <option value="DE">Deutschland</option> <option value="AT">Österreich</option> <option value="CH">Schweiz</option> </select> </div> <div className={styles.formGroup}> <label htmlFor="stateName">Bundesland / Kanton:</label> <select id="stateName" value={stateName} onChange={(e) => setStateName(e.target.value)} disabled={!country || !stateOptions.length}> <option value="">{country ? 'Bitte auswählen...' : '(Zuerst Land wählen)'}</option> {stateOptions.map(state => ( <option key={state} value={state}>{state}</option> ))} </select> </div> </div>
              <div className={styles.formRow}> <div className={styles.formGroup}> <label htmlFor="postalCode">PLZ:</label> <input type="text" id="postalCode" value={postalCode} onChange={(e) => setPostalCode(e.target.value)} autoComplete="postal-code" /> </div> <div className={styles.formGroup}> <label htmlFor="city">Stadt:</label> <input type="text" id="city" value={city} onChange={(e) => setCity(e.target.value)} autoComplete="address-level2" /> </div> </div>
              <div className={styles.formGroup}> <label htmlFor="aboutMe">Über mich:</label> <textarea id="aboutMe" rows="4" value={aboutMe} onChange={(e) => setAboutMe(e.target.value)} /> </div>
              <button type="submit" className={styles.submitButton} disabled={isSavingProfile}> {isSavingProfile ? 'Speichern...' : 'Profil speichern'} </button>
          </form>

          {/* *** GEÄNDERT: Abstand reduziert *** */}
          <hr style={{ margin: '1.5rem 0', border: 0, borderTop: '1px solid #ccc' }} />

          {/* Formular für Bildupload */}
           {/* *** GEÄNDERT: Abstand reduziert *** */}
          <form onSubmit={handleUploadSubmit} style={{ marginBottom: '1.5rem' }}>
              <h3 className={styles.formTitle} style={{ fontSize: '1.5em' }}>Neues Bild hochladen</h3>
              {uploadError && <p className={styles.error}>{uploadError}</p>}
              {uploadSuccess && <p style={{ color: 'green', textAlign: 'center', marginBottom: '10px' }}>Upload erfolgreich!</p>}
              <div className={styles.formGroup}>
                  <label htmlFor="imageUpload" className={styles.fileInputLabel}> Datei auswählen... </label>
                  <input type="file" id="imageUpload" onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
                  {selectedFile && <p style={{ fontSize: '0.9em', marginTop: '10px', color: '#555' }}>Ausgewählt: {selectedFile.name}</p>}
              </div>
              <button type="submit" className={styles.submitButton} disabled={!selectedFile || isUploading} style={{ marginTop: '10px', width: 'auto', padding: '10px 25px', fontSize: '1em' }}>
                  {isUploading ? 'Lädt hoch...' : 'Bild hochladen'}
              </button>
          </form>

           {/* *** GEÄNDERT: Abstand reduziert *** */}
          <hr style={{ margin: '1.5rem 0', border: 0, borderTop: '1px solid #ccc' }} />

          {/* Bereich für hochgeladene Bilder */}
          <div className={styles.imageListContainer}>
              <h3 className={styles.formTitle} style={{ fontSize: '1.5em' }}>Deine Bilder</h3>
              <p style={{ textAlign: 'center', fontSize: '1em', color: '#555', marginBottom: '5px', marginTop: '-15px' }}> Hinweis: Bilder müssen erst durch einen Administrator freigegeben werden. Bitte etwas Geduld. </p>
              <p style={{ textAlign: 'center', fontSize: '1em', color: '#555', marginBottom: '25px' }}> Das erste Bild wird als Haupt-Profilbild verwendet. </p>

              {deleteError && <p className={styles.error}>{deleteError}</p>}
              {imagesLoading && <p style={{textAlign: 'center', padding: '20px'}}>Lade Bilder...</p>}
              {imagesError && <p className={styles.error}>{imagesError}</p>}
              {!imagesLoading && !imagesError && (
                   profileImages.length === 0 ? ( <p style={{textAlign: 'center', padding: '20px', color: '#666'}}>Keine freigegebenen Bilder gefunden.</p> )
                   : ( <div className={styles.imageGrid}> {profileImages.map((image) => ( <div key={image.id} className={styles.imageItem}> <img src={image.image} alt={`Profilbild ${image.id}`} className={styles.profileImage} /> <button onClick={() => handleDeleteImage(image.id)} disabled={deletingImageId === image.id} className={styles.deleteButton} title="Dieses Bild löschen"> {deletingImageId === image.id ? '...' : 'X'} </button> </div> ))} </div> )
              )}
          </div>

      </div>
  );
}

export default ProfileSettingsPage;