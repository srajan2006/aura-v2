import { create } from 'zustand';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface User {
  email: string;
  username: string;
  full_name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      });
      
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      
      const userResponse = await axios.get(`${API_URL}/api/user/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      set({
        token: access_token,
        user: userResponse.data,
        isAuthenticated: true,
      });
    } catch (error) {
      throw new Error('Invalid credentials');
    }
  },

  register: async (email: string, username: string, password: string, fullName: string) => {
    try {
      await axios.post(`${API_URL}/api/auth/register`, {
        email,
        username,
        password,
        full_name: fullName,
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  checkAuth: () => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.get(`${API_URL}/api/user/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(response => {
        set({
          token,
          user: response.data,
          isAuthenticated: true,
        });
      })
      .catch(() => {
        localStorage.removeItem('token');
      });
    }
  },
}));
