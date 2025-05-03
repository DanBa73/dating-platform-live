// frontend/src/App.jsx (Mit Favoriten-Seite und Erhaltene-Likes-Seite)
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

// Layout-Komponente importieren
import Layout from './components/Layout.jsx';

// Seiten-Komponenten importieren
import LandingPage from './pages/LandingPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import ModeratorLoginPage from './pages/ModeratorLoginPage.jsx';
import ModeratorDashboard from './pages/ModeratorDashboard.jsx';
import ModeratorChatPage from './pages/ModeratorChatPage.jsx';
import ProfileSettingsPage from './pages/ProfileSettingsPage.jsx';
import UserProfilePage from './pages/UserProfilePage.jsx';
import UserDashboardPage from './pages/UserDashboardPage.jsx';
import FavoritesPage from './pages/FavoritesPage.jsx';
import ReceivedLikesPage from './pages/ReceivedLikesPage.jsx';
import ConversationsPage from './pages/ConversationsPage.jsx';

// ProtectedRoute importieren
import ProtectedRoute from './components/ProtectedRoute.jsx';


// --- Haupt-App-Komponente ---
function App() {
    return (
        <>
            <Routes>
                {/* Öffentliche Routen (mit Bild-Hintergrund) */}
                <Route path="/" element={<Layout><LandingPage /></Layout>} />
                <Route path="/login" element={<Layout><LoginPage /></Layout>} />
                <Route path="/register" element={<Layout><RegisterPage /></Layout>} />

                {/* Moderator-Login mit Layout und moderatorBackground */}
                <Route path="/mod-login" element={<Layout moderatorBackground><ModeratorLoginPage /></Layout>} />

                {/* Geschützte User-Routen */}
                <Route
                    path="/userdashboard"
                    element={ <ProtectedRoute> <Layout solidBackground> <UserDashboardPage /> </Layout> </ProtectedRoute> }
                />
                <Route
                    path="/profile-settings"
                     // Profil-Einstellungen auch mit solidem Hintergrund? Oder Bild?
                     // Annahme: Bild ist ok hier, da es ein Formular ist. Ansonsten solidBackground hinzufügen.
                    element={ <ProtectedRoute> <Layout> <ProfileSettingsPage /> </Layout> </ProtectedRoute> }
                />
                {/* User Profile */}
                <Route
                    path="/users/:userId/profile" // Korrekter Pfad
                    element={
                        <ProtectedRoute>
                            {/* NEU: solidBackground auch hier hinzugefügt */}
                            <Layout solidBackground>
                                <UserProfilePage />
                            </Layout>
                        </ProtectedRoute>
                     }
                />
                {/* Meine Gespräche Seite */}
                <Route
                    path="/conversations"
                    element={
                        <ProtectedRoute>
                            <Layout solidBackground>
                                <ConversationsPage />
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                {/* Favoriten-Seite */}
                <Route
                    path="/favorites"
                    element={
                        <ProtectedRoute>
                            <Layout solidBackground>
                                <FavoritesPage />
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                {/* Erhaltene Likes Seite */}
                <Route
                    path="/received-likes"
                    element={
                        <ProtectedRoute>
                            <Layout solidBackground>
                                <ReceivedLikesPage />
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                {/* ChatPage Route geschützt und mit Layout */}
                <Route
                    path="/chat/:otherUserId"
                    element={
                        <ProtectedRoute>
                            <Layout solidBackground>
                                <ChatPage />
                            </Layout>
                        </ProtectedRoute>
                    }
                />


                {/* Moderator Routen mit Layout und moderatorBackground */}
                <Route
                    path="/moderator/dashboard"
                    element={ <ProtectedRoute requiresStaff={true}> <Layout moderatorBackground> <ModeratorDashboard /> </Layout> </ProtectedRoute> }
                />
                <Route
                    path="/moderator/chat/:realUserId/:fakeUserId"
                    element={ <ProtectedRoute requiresStaff={true}> <Layout moderatorBackground> <ModeratorChatPage /> </Layout> </ProtectedRoute> }
                />

                {/* Fallback Route? */}
                {/* <Route path="*" element={<NotFoundPage />} /> */}
            </Routes>
        </>
    );
}

export default App;
