// src/App.js

import React, { useState, useEffect } from 'react';
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
  
  const fetchRecommendations = async () => {
    setApiResponse('');
    setError('');
    if (!user) {
      setError("You must be logged in to get recommendations.");
      return;
    }

    try {
      // 1. Get the Firebase ID Token from the current user
      const token = await user.getIdToken();
      
      // 2. Make the request to your Flask backend
      const response = await fetch('http://127.0.0.1:5000/recommend', { // Update with your backend URL
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // 3. Include the token in the Authorization header
          'Authorization': `Bearer ${token}`
        },
      });
      
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }
      
      setApiResponse(JSON.stringify(data, null, 2));

    } catch (err) {
      setError(`API Error: ${err.message}`);
      console.error("API Fetch Error:", err);
    }
  };


  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>AniCenter 🚀</h1>
      {!user ? (
        <div>
          <h2>Login / Sign Up</h2>
          <form>
            {/* Add Username Input Field */}
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" /><br /><br />
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" /><br /><br />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" /><br /><br />
            <button onClick={handleLogin}>Login</button>
            <button onClick={handleSignUp} style={{ marginLeft: '10px' }}>Sign Up</button>
          </form>
        </div>
      ) : (
        <div>
          <h2>Welcome, {user.email}!</h2>
          <p>Firebase UID: {user.uid}</p>
          <button onClick={handleLogout}>Logout</button>
          <hr style={{ margin: '20px 0' }}/>
          <button onClick={fetchRecommendations}>Get My Recommendations</button>
        </div>
      )}

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