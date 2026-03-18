// src/App.js

import React, { useState, useEffect, useCallback } from 'react';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
  signOut
} from "firebase/auth";
import { auth } from './firebaseConfig.js'; // Import the auth instance

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState(null); // To hold the authenticated user object
  const [apiResponse, setApiResponse] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [animeList, setAnimeList] = useState([]);
  const [userRatings, setUserRatings] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  
  // Listen for authentication state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        console.log("User is logged in:", currentUser);
      } else {
        console.log("User is logged out.");
      }
    });
    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    if (!username) {
        setError("Please enter a username.");
        return;
    }

    try {
      // Step 1: Create user in Firebase Auth
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const firebaseUser = userCredential.user;
      console.log("Firebase user created:", firebaseUser);

      // Step 2: Get the token and sync the profile to your backend
      const token = await firebaseUser.getIdToken();

      const response = await fetch('http://127.0.0.1:5000/users/sync', { // Your new endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ username: username }) // Send the username
      });

      const data = await response.json();
      if (!response.ok) {
        // If sync fails, it's good practice to delete the Firebase user to allow a retry
        // await firebaseUser.delete(); // Consider this for production robustness
        throw new Error(data.error || "Failed to sync user profile.");
      }
      
      console.log("Backend sync successful:", data);

    } catch (err) {
      setError(err.message);
      console.error("Signup or Sync Error:", err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err) {
      setError(err.message);
      console.error("Login Error:", err);
    }
  };

  const handleLogout = async () => {
    setError('');
    try {
      await signOut(auth);
      setApiResponse(''); // Clear previous API responses
    } catch (err) {
      setError(err.message);
      console.error("Logout Error:", err);
    }
  };
  
  const loadAnimeList = useCallback(async () => {
    try {
      const token = await user.getIdToken();
      // Add small delay to prevent "token used too early" error
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const response = await fetch('http://127.0.0.1:5000/anime', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnimeList(data.anime || []);
        // Initialize ratings for all anime as 0
        const initialRatings = {};
        data.anime.forEach(anime => {
          initialRatings[anime.mal_id] = 0;
        });
        setUserRatings(initialRatings);
      }
    } catch (err) {
      setError(`Error loading anime: ${err.message}`);
    }
  }, [user]);

  const handleRatingChange = async (animeId, newRating) => {
    try {
      const token = await user.getIdToken();
      
      const response = await fetch(`http://127.0.0.1:5000/ratings/anime/${animeId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ score: newRating })
      });
      
      if (response.ok) {
        setUserRatings(prev => ({
          ...prev,
          [animeId]: newRating
        }));
      } else {
        setError(`Error rating anime: ${response.statusText}`);
      }
    } catch (err) {
      setError(`Error rating anime: ${err.message}`);
    }
  };

  const fetchContentRecommendations = async () => {
    try {
      const token = await user.getIdToken();
      
      const response = await fetch('http://127.0.0.1:5000/recommender/content-recommendations', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
    } catch (err) {
      setError(`Error getting recommendations: ${err.message}`);
    }
  };

  // Load anime list when user logs in
  useEffect(() => {
    if (user && animeList.length === 0) {
      loadAnimeList();
    }
  }, [user, animeList.length, loadAnimeList]);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>AniCenter 🚀</h1>
      {!user ? (
        <div>
          <h2>Login / Sign Up</h2>
          <form>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" /><br /><br />
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" /><br /><br />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" /><br /><br />
            <button onClick={handleLogin}>Login</button>
            <button onClick={handleSignUp} style={{ marginLeft: '10px' }}>Sign Up</button>
          </form>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '20px' }}>
          {/* Left Panel - Anime List with Ratings */}
          <div style={{ flex: 1, border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}>
            <h3>Anime List</h3>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {animeList.map(anime => (
                <div key={anime.mal_id} style={{ marginBottom: '10px', padding: '5px', borderBottom: '1px solid #eee' }}>
                  <div style={{ fontWeight: 'bold' }}>{anime.title}</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>ID: {anime.mal_id}</div>
                  <div style={{ display: 'flex', alignItems: 'center', marginTop: '5px' }}>
                    <span style={{ marginRight: '10px', fontSize: '14px' }}>Rating:</span>
                    <input 
                      type="range" 
                      min="0" 
                      max="10" 
                      value={userRatings[anime.mal_id] || 0}
                      onChange={(e) => handleRatingChange(anime.mal_id, parseInt(e.target.value))}
                      style={{ flex: 1, marginRight: '10px' }}
                    />
                    <span style={{ fontSize: '14px', fontWeight: 'bold', minWidth: '20px' }}>
                      {userRatings[anime.mal_id] || 0}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel - Recommendations */}
          <div style={{ flex: 1, border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h3>Recommendations</h3>
              <button onClick={fetchContentRecommendations} style={{ padding: '5px 10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer' }}>
                Get Recommendations
              </button>
            </div>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {recommendations.map(animeId => {
                const anime = animeList.find(a => a.mal_id === animeId);
                return anime ? (
                  <div key={animeId} style={{ marginBottom: '10px', padding: '5px', borderBottom: '1px solid #eee' }}>
                    <div style={{ fontWeight: 'bold' }}>{anime.title}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>ID: {animeId}</div>
                  </div>
                ) : null;
              })}
            </div>
          </div>
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <button onClick={handleLogout}>Logout</button>
      </div>

      {error && <pre style={{ color: 'red', marginTop: '20px' }}>{error}</pre>}
      {apiResponse && 
        <div style={{ marginTop: '20px' }}>
          <h3>Backend Response:</h3>
          <pre style={{ background: '#f0f0f0', padding: '10px', borderRadius: '5px' }}>
            <code>{apiResponse}</code>
          </pre>
        </div>
      }
    </div>
  );

}

export default App;