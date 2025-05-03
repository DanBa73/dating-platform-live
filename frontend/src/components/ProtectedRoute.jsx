// frontend/src/components/ProtectedRoute.jsx (Überarbeitet)

import React, { useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';

// NEU: Nimmt jetzt eine optionale 'requiresStaff' Prop entgegen
function ProtectedRoute({ children, requiresStaff = false }) {
    const { isAuthenticated, user, isAuthLoading } = useContext(AuthContext);
    const location = useLocation();

    // --- DEBUGGING LOGS (können später entfernt werden) ---
    console.log("--- ProtectedRoute Check ---");
    console.log("  Pathname:", location.pathname);
    console.log("  Requires Staff:", requiresStaff); // Zeigt an, ob Staff nötig ist
    console.log("  isAuthLoading:", isAuthLoading);
    console.log("  isAuthenticated:", isAuthenticated);
    console.log("  user?.is_staff:", user?.is_staff);
    // --- END DEBUGGING ---

    // 1. Warte, wenn der Auth-Status noch lädt
    if (isAuthLoading) {
        console.log("ProtectedRoute: Status: Loading...");
        return <div>Prüfe Authentifizierung...</div>; // Oder ein schönerer Loader
    }

    // 2. Prüfe, ob überhaupt eingeloggt
    if (!isAuthenticated) {
        console.log("ProtectedRoute: Status: Not Authenticated. Redirecting to /login.");
        // Nicht eingeloggt -> zum Login schicken, ursprüngliches Ziel merken
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    // 3. Prüfe, ob Staff-Rechte erforderlich SIND, aber der User sie NICHT hat
    if (requiresStaff && !user?.is_staff) {
        console.log("ProtectedRoute: Status: Staff required but user is not staff. Redirecting to /userdashboard.");
        // Eingeloggt, aber keine Admin-Rechte für diese Seite -> zum User-Dashboard
        // Alternativ könnte man auch zu einer "Kein Zugriff"-Seite leiten
        return <Navigate to="/userdashboard" replace />;
    }

    // 4. Wenn eingeloggt UND (entweder kein Staff nötig ODER User ist Staff) -> Zugriff erlauben
    console.log("ProtectedRoute: Status: Access GRANTED.");
    return children;
}

export default ProtectedRoute;