// frontend/src/pages/UserDashboardPage.jsx (Mit ActivitySummary)
import React, { useContext, useEffect, useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';
import ActivitySummary from '../components/ActivitySummary.jsx';
import styles from './UserDashboardPage.module.css';

// Daten für abhängige Dropdowns
const countryStateData = {
    DE: ['Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen'],
    AT: ['Burgenland', 'Kärnten', 'Niederösterreich', 'Oberösterreich', 'Salzburg', 'Steiermark', 'Tirol', 'Vorarlberg', 'Wien'],
    CH: ['Aargau', 'Appenzell Ausserrhoden', 'Appenzell Innerrhoden', 'Basel-Landschaft', 'Basel-Stadt', 'Bern', 'Freiburg', 'Genf', 'Glarus', 'Graubünden', 'Jura', 'Luzern', 'Neuenburg', 'Nidwalden', 'Obwalden', 'Schaffhausen', 'Schwyz', 'Solothurn', 'St. Gallen', 'Tessin', 'Thurgau', 'Uri', 'Waadt', 'Wallis', 'Zug', 'Zürich']
};

function UserDashboardPage() {
    const { user, isProfileComplete, isAuthLoading, authToken } = useContext(AuthContext);
    const navigate = useNavigate();

    // States für Vorschläge
    const [suggestions, setSuggestions] = useState([]);
    const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [errorSuggestions, setErrorSuggestions] = useState(null);
    const [nextPageUrl, setNextPageUrl] = useState(null);

    // States für Filterwerte
    const [filterCountryInput, setFilterCountryInput] = useState('');
    const [filterStateInput, setFilterStateInput] = useState('');
    const [filterCityInput, setFilterCityInput] = useState('');
    const [filterPlzInput, setFilterPlzInput] = useState('');
    const [stateFilterOptions, setStateFilterOptions] = useState([]);

    // States für angewendete Filter
    const [appliedFilters, setAppliedFilters] = useState({ country: '', state: '', city: '', plz: '' });

    // useEffect zum Aktualisieren der Bundesland-Optionen
    useEffect(() => { if (filterCountryInput && countryStateData[filterCountryInput]) { setStateFilterOptions(countryStateData[filterCountryInput]); } else { setStateFilterOptions([]); } }, [filterCountryInput]);

    // useEffect für Profil-Check
    useEffect(() => { if (!isAuthLoading) { if (!isProfileComplete) { navigate('/profile-settings', { replace: true }); } } }, [isAuthLoading, isProfileComplete, navigate]);

    // Zentrale Funktion zum Laden der Vorschläge
    const fetchSuggestions = useCallback(async (url, isInitialLoad = false) => { /* ... (unverändert) ... */ if (!authToken) return; if (isInitialLoad) { setIsLoadingSuggestions(true); } else { setIsLoadingMore(true); } setErrorSuggestions(null); try { const response = await fetch(url, { method: 'GET', headers: { 'Authorization': `Token ${authToken}`, 'Content-Type': 'application/json' }, }); if (response.ok) { const data = await response.json(); if (isInitialLoad) { setSuggestions(data.results); } else { setSuggestions(prev => [...prev, ...data.results]); } setNextPageUrl(data.next); } else { let errorMsg = `Fehler ${response.status}`; try { const errorData = await response.json(); errorMsg = errorData.detail || JSON.stringify(errorData); } catch (e) { /* ignore */ } setErrorSuggestions(`Vorschläge konnten nicht geladen werden: ${errorMsg}`); setNextPageUrl(null); } } catch (err) { setErrorSuggestions("Netzwerkfehler beim Laden der Vorschläge."); setNextPageUrl(null); } finally { if (isInitialLoad) { setIsLoadingSuggestions(false); } else { setIsLoadingMore(false); } } }, [authToken]);

    // Initiales Laden & Laden bei Filter-Änderung
    useEffect(() => { if (!isAuthLoading && isProfileComplete && authToken) { const params = new URLSearchParams(); if (appliedFilters.country) params.append('country', appliedFilters.country); if (appliedFilters.state) params.append('state', appliedFilters.state); if (appliedFilters.city) params.append('city', appliedFilters.city); if (appliedFilters.plz) params.append('plz', appliedFilters.plz); const baseUrl = 'http://127.0.0.1:8000/api/accounts/suggestions/'; const urlWithParams = `${baseUrl}?${params.toString()}`; fetchSuggestions(urlWithParams, true); } }, [isAuthLoading, isProfileComplete, authToken, appliedFilters, fetchSuggestions]);

    // Funktion zum Laden weiterer Vorschläge
    const loadMoreSuggestions = useCallback(() => { if (nextPageUrl && !isLoadingMore) { fetchSuggestions(nextPageUrl, false); } }, [nextPageUrl, isLoadingMore, fetchSuggestions]);

    // Handler zum Anwenden der Filter
    const handleApplyFilters = () => { setAppliedFilters({ country: filterCountryInput, state: filterStateInput, city: filterCityInput, plz: filterPlzInput }); };

    // Handler für Länder-Dropdown-Änderung
    const handleCountryFilterChange = (event) => { setFilterCountryInput(event.target.value); setFilterStateInput(''); };

    // Lade-/Prüfzustand für Profil
    if (isAuthLoading || !isProfileComplete) { return <div className={styles.loadingMessage}>Profil wird geprüft...</div>; }

    // renderSuggestions (unverändert)
    const renderSuggestions = () => { /* ... (wie vorher) ... */ if (isLoadingSuggestions && suggestions.length === 0) { return <p className={styles.loadingMessage}>Lade Vorschläge...</p>; } if (errorSuggestions && !isLoadingMore) { return <p className={`${styles.errorMessage}`}>{errorSuggestions}</p>; } if (!isLoadingSuggestions && suggestions.length === 0 && !errorSuggestions) { return <p className={styles.infoMessage}>Keine passenden Vorschläge gefunden.</p>; } return ( <div className={styles.suggestionGrid}> {suggestions.map(suggestion => ( <Link to={`/users/${suggestion.id}/profile`} key={suggestion.id} className={styles.suggestionCardLink}> <div className={styles.suggestionCard}> <div className={styles.profilePicContainer}> {suggestion.profile_picture_url ? ( <img src={suggestion.profile_picture_url} alt={`Profilbild von ${suggestion.username}`} className={styles.profilePic} /> ) : ( <div className={styles.profilePicPlaceholder}>?</div> )} </div> <div className={styles.userInfo}> <span className={styles.username}>{suggestion.username}</span> <span className={styles.details}> {suggestion.age ? `${suggestion.age}` : '-'} {' | '} {suggestion.city || '-'} </span> </div> </div> </Link> ))} </div> ); };

    // Haupt-Return für das Dashboard
    return (
        <div className={styles.dashboardContainer}>
            <h1 className={styles.dashboardTitle}>Benutzer Dashboard</h1>
            <p className={styles.dashboardSubtitle}>Willkommen zurück, {user?.username}!</p>

            {/* ActivitySummary-Komponente */}
            <ActivitySummary />

            {/* Filter-Bereich */}
            <div className={styles.filterContainer}>
                {/* Optional: Überschrift für Filter? */}
                {/* <h3>Filter</h3> */}
                <div className={styles.filterGroup}>
                    <label htmlFor="filterCountry">Land:</label>
                    <select id="filterCountry" value={filterCountryInput} onChange={handleCountryFilterChange} className={styles.filterSelect} > <option value="">Alle Länder</option> <option value="DE">Deutschland</option> <option value="AT">Österreich</option> <option value="CH">Schweiz</option> </select>
                </div>
                <div className={styles.filterGroup}>
                    <label htmlFor="filterState">Bundesland:</label>
                    <select id="filterState" value={filterStateInput} onChange={(e) => setFilterStateInput(e.target.value)} disabled={!filterCountryInput || !stateFilterOptions.length} className={styles.filterSelect} > <option value="">{filterCountryInput ? 'Alle Bundesländer' : '(Zuerst Land wählen)'}</option> {stateFilterOptions.map(state => ( <option key={state} value={state}>{state}</option> ))} </select>
                </div>
                <div className={styles.filterGroup}>
                    <label htmlFor="filterCity">Stadt:</label>
                    <input type="text" id="filterCity" value={filterCityInput} onChange={(e) => setFilterCityInput(e.target.value)} placeholder="z.B. Mitte" className={styles.filterInput} />
                </div>
                <div className={styles.filterGroup}>
                    <label htmlFor="filterPlz">PLZ (Anfang):</label>
                    <input type="text" id="filterPlz" value={filterPlzInput} onChange={(e) => setFilterPlzInput(e.target.value)} placeholder="z.B. 10" className={styles.filterInput} />
                </div>
                <button onClick={handleApplyFilters} className={styles.filterButton}> Filter anwenden </button>
            </div>

            <h2 className={styles.sectionTitle}>Treffer</h2>
            {renderSuggestions()}

             {/* Button zum Nachladen */}
             {nextPageUrl && ( <button className={styles.loadMoreButton} onClick={loadMoreSuggestions} disabled={isLoadingMore} > {isLoadingMore ? 'Lade mehr...' : 'Mehr laden'} </button> )}
             {isLoadingMore && <p className={styles.loadingMessage}>Lade weitere Vorschläge...</p>}
        </div>
    );
}

export default UserDashboardPage;
