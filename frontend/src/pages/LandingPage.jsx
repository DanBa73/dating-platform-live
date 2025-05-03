// frontend/src/pages/LandingPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // NEU: useNavigate importieren
import styles from './LandingPage.module.css'; // Eigenes CSS für LandingPage-Inhalte


function LandingPage() {
  const [selectedGender, setSelectedGender] = useState(null); // 'MALE' oder 'FEMALE'
  const [selectedSeeking, setSelectedSeeking] = useState(null); // 'MALE' oder 'FEMALE'

  const navigate = useNavigate(); // NEU: Hook für Navigation holen

  const handleGenderSelect = (gender) => {
    setSelectedGender(gender);
  };

  const handleSeekingSelect = (seeking) => {
    setSelectedSeeking(seeking);
  };

  // NEU: Handler für den Klick auf den Hauptbutton
  const handleFindProfilesClick = () => {
    // Nur navigieren, wenn beides ausgewählt ist
    if (selectedGender && selectedSeeking) {
      // Zur Registrierungsseite navigieren und Auswahl als URL-Parameter mitgeben
      navigate(`/register?gender=${selectedGender}&seeking=${selectedSeeking}`);
    } else {
      // Optional: Hinweis für den Benutzer, falls noch etwas fehlt
      alert('Bitte wähle zuerst aus, wer du bist und wen du suchst.');
    }
  };
  // ENDE NEU

  return (
    <main className={styles.landingMainContent}>

      <h1 className={styles.landingHeadline}>
        Finde noch heute dein Date! Tausende Mitglieder sind schon dabei und warten auf dich!
      </h1>

      <div className={styles.landingBox}>

        <div className={styles.genderSelection}>
          <label>Ich bin ein(e):</label>
          <div className={styles.options}>
            <button
              type="button"
              className={`${styles.optionsButton} ${selectedGender === 'MALE' ? styles.activeOption : ''}`}
              onClick={() => handleGenderSelect('MALE')}
            >
              MANN
            </button>
            <button
              type="button"
              className={`${styles.optionsButton} ${selectedGender === 'FEMALE' ? styles.activeOption : ''}`}
              onClick={() => handleGenderSelect('FEMALE')}
            >
              FRAU
            </button>
          </div>
        </div>

        <div className={styles.seekingSelection}>
          <label>auf der Suche nach:</label>
          <div className={styles.options}>
             {/* Werte MALE/FEMALE für die Speicherung im State und Übergabe an URL */}
            <button
              type="button"
              className={`${styles.optionsButton} ${selectedSeeking === 'MALE' ? styles.activeOption : ''}`}
              onClick={() => handleSeekingSelect('MALE')}
            >
              MÄNNERN
            </button>
            <button
              type="button"
              className={`${styles.optionsButton} ${selectedSeeking === 'FEMALE' ? styles.activeOption : ''}`}
              onClick={() => handleSeekingSelect('FEMALE')}
            >
              FRAUEN
            </button>
          </div>
        </div>

         {/* NEU: onClick und disabled hinzugefügt */}
        <button
          type="button"
          className={styles.findButton}
          onClick={handleFindProfilesClick}
          disabled={!selectedGender || !selectedSeeking} // Button ist deaktiviert, bis beides ausgewählt ist
        >
          PROFILE FINDEN
        </button>
         {/* ENDE NEU */}
      </div>

      <p className={styles.landingFooterText}>
        KOSTENLOSE Registrierung! KEIN Abo! Dein Date wartet!
      </p>

    </main>
  );
}

export default LandingPage;