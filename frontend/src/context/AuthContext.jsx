// frontend/src/context/AuthContext.jsx (mit refreshAuthUser Funktion)

import React, { createContext, useState, useEffect, useCallback } from 'react';

export const AuthContext = createContext(null);
const API_BASE_URL = 'http://127.0.0.1:8000';

export const AuthProvider = ({ children }) => {
    const [authToken, setAuthToken] = useState(() => localStorage.getItem('authToken'));
    const [user, setUser] = useState(null);
    const [isAuthLoading, setIsAuthLoading] = useState(true);
    const [isProfileComplete, setIsProfileComplete] = useState(false);

    const logout = useCallback(() => {
        console.log("AuthContext: Logging out...");
        localStorage.removeItem('authToken');
        setAuthToken(null);
        setUser(null);
        setIsProfileComplete(false);
    }, []);

    const fetchUserDetails = useCallback(async (token) => {
        console.log("AuthContext: Attempting fetch user details. Token:", !!token);
        if (!token) { setUser(null); setIsProfileComplete(false); setIsAuthLoading(false); return; }

        try {
            const apiUrl = `${API_BASE_URL}/api/auth/user/`;
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: { 'Authorization': `Token ${token}`, 'Content-Type': 'application/json' },
            });
            if (response.ok) {
                const userData = await response.json();
                console.log("AuthContext: User details fetched:", userData);
                setUser(userData);
                const profileCompleteCheck = !!(userData.country && userData.city && userData.postal_code); // Prüfe relevante Felder
                setIsProfileComplete(profileCompleteCheck);
                console.log("AuthContext: Profile complete status set to:", profileCompleteCheck);
            } else {
                console.error(`AuthContext: Failed user fetch, status: ${response.status}`);
                logout();
            }
        } catch (error) {
            console.error("AuthContext: Network error fetching user details:", error);
            logout();
        } finally {
             if (isAuthLoading) { setIsAuthLoading(false); }
        }
    }, [logout, isAuthLoading]); // isAuthLoading Abhängigkeit prüfen


    useEffect(() => {
        const initialToken = localStorage.getItem('authToken');
        console.log("AuthContext: Initial load. Token:", !!initialToken);
        if (initialToken) { fetchUserDetails(initialToken); }
        else { setIsAuthLoading(false); setIsProfileComplete(false); }
    }, [fetchUserDetails]); // fetchUserDetails als Abhängigkeit ist korrekt dank useCallback


    const login = (token) => {
        console.log("AuthContext: login function called.");
        localStorage.setItem('authToken', token);
        setAuthToken(token);
        fetchUserDetails(token);
    };

    const registerUser = async (registrationData) => {
        console.log("AuthContext: Attempting registration...");
        const apiUrl = `${API_BASE_URL}/api/auth/registration/`;
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify(registrationData),
            });
            if (response.ok) {
                console.log("AuthContext: Registration successful:", await response.json());
                return true;
            } else {
                const errorData = await response.json();
                console.error(`AuthContext: Registration failed, status: ${response.status}`, errorData);
                throw new Error(JSON.stringify(errorData) || `Request failed with status ${response.status}`);
            }
        } catch (error) {
            console.error("AuthContext: Network or other error during registration:", error);
            throw error;
        }
    };

    // --- NEU: Funktion zum Neuladen der User-Daten ---
    const refreshAuthUser = useCallback(async () => {
        const currentToken = authToken || localStorage.getItem('authToken'); // Nimm aktuellen Token
        if (currentToken) {
            console.log("AuthContext: Refreshing user details explicitly...");
            // Setze Loading kurz true, damit abhängige Komponenten neu rendern, während Daten geladen werden
            // setIsAuthLoading(true); // Vorsicht: Könnte zu Flackern führen, evtl. weglassen
            await fetchUserDetails(currentToken); // Rufe die bestehende Fetch-Logik auf
        } else {
            console.log("AuthContext: Cannot refresh user, no token available.");
        }
    }, [authToken, fetchUserDetails]); // Abhängig von Token und der (stabilen) fetch-Funktion
    // --- ENDE NEU ---


    // Context Value erweitert
    const contextValue = {
        authToken,
        user,
        isAuthLoading,
        isAuthenticated: !!authToken && !!user,
        isProfileComplete,
        login,
        logout,
        registerUser,
        refreshAuthUser, // NEU: Funktion hinzugefügt
    };

    return (
        <AuthContext.Provider value={contextValue}>
            {!isAuthLoading ? children : <div>Loading Authentication...</div>}
        </AuthContext.Provider>
    );
};