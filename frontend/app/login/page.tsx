"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await login(formData.email, formData.password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials.");
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Montserrat:wght@300;400;500&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        .auth-page {
          min-height: 100vh;
          background: #0a0a0a;
          color: #f0ebe3;
          font-family: 'Montserrat', sans-serif;
          display: grid;
          grid-template-columns: 1fr 1fr;
        }

        /* Left panel */
        .auth-left {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 3rem 4rem;
          border-right: 1px solid #1a1a1a;
          position: relative;
          overflow: hidden;
        }

        .auth-left::before {
          content: '';
          position: absolute;
          bottom: -100px;
          left: -100px;
          width: 400px;
          height: 400px;
          background: radial-gradient(circle, #c9a84c0a 0%, transparent 70%);
          pointer-events: none;
        }

        .logo {
          font-family: 'Playfair Display', serif;
          font-size: 1.8rem;
          font-weight: 900;
          letter-spacing: 0.4em;
          color: #f0ebe3;
          text-transform: uppercase;
          cursor: pointer;
        }
        .logo span { color: #c9a84c; }

        .left-content { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 4rem 0; }

        .left-tag {
          font-size: 0.55rem;
          letter-spacing: 0.35em;
          text-transform: uppercase;
          color: #c9a84c;
          margin-bottom: 2rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          font-weight: 500;
        }
        .left-tag::before {
          content: '';
          display: inline-block;
          width: 30px;
          height: 1px;
          background: #c9a84c;
        }

        .left-title {
          font-family: 'Playfair Display', serif;
          font-size: clamp(2.5rem, 4vw, 4rem);
          font-weight: 900;
          line-height: 1;
          color: #f0ebe3;
          margin-bottom: 1.5rem;
        }
        .left-title em { font-style: italic; color: #c9a84c; display: block; }

        .left-body {
          font-family: 'Cormorant Garamond', serif;
          font-style: italic;
          font-size: 1.05rem;
          color: #555;
          line-height: 1.9;
          max-width: 320px;
        }

        .left-footer {
          font-size: 0.5rem;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #2a2a2a;
        }

        /* Right panel — form */
        .auth-right {
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 3rem 4rem;
        }

        .form-head { margin-bottom: 3rem; }
        .form-title {
          font-family: 'Playfair Display', serif;
          font-size: 2rem;
          font-weight: 900;
          color: #f0ebe3;
          margin-bottom: 0.5rem;
        }
        .form-sub {
          font-size: 0.6rem;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: #444;
          font-weight: 500;
        }

        .form { display: flex; flex-direction: column; gap: 1.5rem; }

        .field { display: flex; flex-direction: column; gap: 0.5rem; }

        .field-label {
          font-size: 0.55rem;
          letter-spacing: 0.25em;
          text-transform: uppercase;
          color: #c9a84c;
          font-weight: 500;
        }

        .field-input {
          background: transparent;
          border: none;
          border-bottom: 1px solid #1e1e1e;
          padding: 0.75rem 0;
          color: #f0ebe3;
          font-size: 0.95rem;
          font-family: 'Montserrat', sans-serif;
          font-weight: 300;
          outline: none;
          transition: border-color 0.3s;
          width: 100%;
        }
        .field-input::placeholder { color: #333; }
        .field-input:focus { border-bottom-color: #c9a84c; }

        .error-msg {
          font-size: 0.6rem;
          letter-spacing: 0.1em;
          color: #e05555;
          padding: 0.75rem 1rem;
          border: 1px solid #e0555522;
          background: #e055550a;
        }

        .submit-btn {
          margin-top: 1rem;
          padding: 1.1rem;
          background: #f0ebe3;
          color: #0a0a0a;
          font-size: 0.65rem;
          letter-spacing: 0.25em;
          text-transform: uppercase;
          font-family: 'Montserrat', sans-serif;
          font-weight: 500;
          border: none;
          cursor: pointer;
          transition: background 0.3s;
        }
        .submit-btn:hover { background: #c9a84c; }
        .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .form-footer {
          margin-top: 2rem;
          font-size: 0.6rem;
          letter-spacing: 0.1em;
          color: #444;
          text-transform: uppercase;
        }
        .form-link {
          color: #f0ebe3;
          cursor: pointer;
          text-decoration: none;
          transition: color 0.3s;
        }
        .form-link:hover { color: #c9a84c; }

        /* Animations */
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .fade-1 { animation: fadeUp 0.7s ease forwards; }
        .fade-2 { animation: fadeUp 0.7s 0.15s ease forwards; opacity: 0; }

        @media (max-width: 768px) {
          .auth-page { grid-template-columns: 1fr; }
          .auth-left { display: none; }
          .auth-right { padding: 3rem 2rem; }
        }
      `}</style>

      <div className="auth-page">
        {/* Left */}
        <div className="auth-left fade-1">
          <div className="logo" onClick={() => router.push('/')}>AUR<span>A</span></div>
          <div className="left-content">
            <div className="left-tag">Welcome Back</div>
            <h2 className="left-title">Your style<br /><em>awaits.</em></h2>
            <p className="left-body">
              Sign in to access your curated wardrobe and today's outfit recommendations.
            </p>
          </div>
          <div className="left-footer">© 2024 Aura — Fashion Intelligence</div>
        </div>

        {/* Right */}
        <div className="auth-right fade-2">
          <div className="form-head">
            <div className="form-title">Sign In</div>
            <div className="form-sub">Enter your credentials to continue</div>
          </div>

          <form className="form" onSubmit={handleSubmit}>
            <div className="field">
              <label className="field-label">Email Address</label>
              <input
                type="email"
                className="field-input"
                placeholder="you@example.com"
                value={formData.email}
                onChange={e => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
            <div className="field">
              <label className="field-label">Password</label>
              <input
                type="password"
                className="field-input"
                placeholder="••••••••"
                value={formData.password}
                onChange={e => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>

            {error && <div className="error-msg">{error}</div>}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? "Signing in..." : "Sign In →"}
            </button>
          </form>

          <div className="form-footer">
            No account?{" "}
            <a className="form-link" onClick={() => router.push('/register')}>Create one</a>
          </div>
        </div>
      </div>
    </>
  );
}
