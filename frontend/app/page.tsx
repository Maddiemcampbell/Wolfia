"use client";

import React, { useEffect, useState } from 'react';
import { api } from "@/api";
import { UserResponse } from "@/api/data-contracts";

export default function Home() {
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);
  const [impersonatedUser, setImpersonatedUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clientId, setClientId] = useState('');
  const [impersonatorName, setImpersonatorName] = useState<string | null>(null);
  const [impersonatorLoading, setImpersonatorLoading] = useState(true);

  const fetchUserSession = async () => {
    try {
      const sessionResponse = await api.get('/auth/session');
      setImpersonatorName(sessionResponse.data.impersonator_name);
    } catch (error) {
      console.error('Error fetching user session:', error);
    } finally {
      setImpersonatorLoading(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      setImpersonatorLoading(true);
      try {
        const currentUserResponse = await api.get<UserResponse>('/auth/me');
        setCurrentUser(currentUserResponse.data);
        await fetchUserSession(); // Fetch session immediately after fetching current user
      } catch (error) {
        setError('Error fetching data');
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleImpersonate = async () => {
    if (!currentUser) return;
    try {
      const response = await api.post<{ token: string }>('/auth/impersonate', {
        client_user_id: clientId,
        impersonator_id: currentUser.id,
      });
      const impersonatedResponse = await api.get<UserResponse>('/auth/me');
      setImpersonatedUser(impersonatedResponse.data);
      await fetchUserSession();
    } catch (error) {
      setError('Error impersonating user');
      console.error('Error impersonating user:', error);
    }
  };

  const handleStopImpersonation = async () => {
    try {
      const stopResponse = await api.post('/auth/stop_impersonation');
      setImpersonatedUser(null);
      setImpersonatorName(null);
      const response = await api.get<UserResponse>('/auth/me');
      setCurrentUser(response.data);
    } catch (error) {
      setError('Error stopping impersonation');
      console.error('Error stopping impersonation:', error);
    }
  };

  if (loading || impersonatorLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm lg:flex">
          <h2>Loading...</h2>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm lg:flex">
          <h2>{error}</h2>
        </div>
      </main>
    );
  }

  if (!currentUser) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm lg:flex">
          <h2>Unable to fetch user data. Please try again later.</h2>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        {currentUser && (
          <div>
            <h2>
              <strong>Welcome home, {impersonatedUser ? impersonatedUser.name : currentUser.name}!</strong>
              {impersonatorName && (
                <span> *Wolfia internal user {impersonatorName} is impersonating*</span>
              )}
            </h2>
            <p><strong>Email:</strong> {impersonatedUser ? impersonatedUser.email : currentUser.email}</p>
            <p><strong>Organization:</strong> {impersonatedUser ? impersonatedUser.organization_name : currentUser.organization_name}</p>
            <p><strong>Admin:</strong> {currentUser.is_internal ? 'Yes' : 'No'}</p>
            <p><strong>Member since:</strong> {new Date(currentUser.created_at).toLocaleDateString()}</p>
          </div>
        )}
        {currentUser && currentUser.is_internal && !impersonatorName && (
          <div>
            <h3>Debugging Mode - Impersonate a Client</h3>
            <input
              type="text"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              placeholder="Client User ID"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
            />
            <button
              onClick={handleImpersonate}
              className="mt-2 py-2 px-4 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Impersonate
            </button>
          </div>
        )}
        {impersonatorName && (
          <button
            onClick={handleStopImpersonation}
            className="mt-2 py-2 px-4 bg-red-600 text-white font-medium rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Stop Impersonating
          </button>
        )}
      </div>
    </main>
  );
}
