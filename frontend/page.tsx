'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Montserrat:wght@300;400;500&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        .landing {
          min-height: 100vh;
          background: #0a0a0a;
          color: #f0ebe3;
          font-family: 'Montserrat', sans-serif;
          display: grid;
          grid-template-rows: auto 1fr auto;
          position: relative;
          overflow: hidden;
        }

        /* Grain texture overlay */
        .landing::before {
          content: '';
          position: fixed;
          inset: 0;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
          pointer-events: none;
          z-index: 1;
          opacity: 0.4;
        }

        /* Vertical gold line */
        .gold-line {
          position: fixed;
          left: 50%;
          top: 0;
          width: 1px;
          height: 100vh;
          background: linear-gradient(to bottom, transparent, #c9a84c22, transparent);
          pointer-events: none;
          z-index: 0;
        }

        /* Header */
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 2.5rem 4rem;
          border-bottom: 1px solid #1a1a1a;
          position: relative;
          z-index: 10;
        }
        .logo {
          font-family: 'Playfair Display', serif;
          font-size: 1.6rem;
          font-weight: 900;
          letter-spacing: 0.4em;
          color: #f0ebe3;
          text-transform: uppercase;
        }
        .logo span { color: #c9a84c; }
        .header-tagline {
          font-size: 0.55rem;
          letter-spacing: 0.3em;
          text-transform: uppercase;
          color: #444;
          font-weight: 500;
        }

        /* Hero */
        .hero {
          display: grid;
          grid-template-columns: 1fr 1fr;
          position: relative;
          z-index: 10;
        }

        .hero-left {
          padding: 5rem 4rem 5rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          border-right: 1px solid #1a1a1a;
        }

        .issue-tag {
          font-size: 0.55rem;
          letter-spacing: 0.35em;
          text-transform: uppercase;
          color: #c9a84c;
          margin-bottom: 2.5rem;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .issue-tag::before {
          content: '';
          display: inline-block;
          width: 30px;
          height: 1px;
          background: #c9a84c;
        }

        .hero-title {
          font-family: 'Playfair Display', serif;
          font-size: clamp(4rem, 8vw, 7.5rem);
          font-weight: 900;
          line-height: 0.9;
          color: #f0ebe3;
          margin-bottom: 2.5rem;
          letter-spacing: -0.02em;
        }
        .hero-title em {
          font-style: italic;
          color: #c9a84c;
          display: block;
        }

        .hero-body {
          font-family: 'Cormorant Garamond', serif;
          font-size: 1.15rem;
          color: #666;
          line-height: 1.9;
          font-style: italic;
          max-width: 380px;
          margin-bottom: 3.5rem;
        }

        .hero-actions { display: flex; flex-direction: column; gap: 1rem; max-width: 280px; }

        .btn-primary {
          padding: 1.1rem 2.5rem;
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
          text-align: center;
        }
        .btn-primary:hover { background: #c9a84c; }

        .btn-secondary {
          padding: 1.1rem 2.5rem;
          background: transparent;
          color: #555;
          font-size: 0.65rem;
          letter-spacing: 0.25em;
          text-transform: uppercase;
          font-family: 'Montserrat', sans-serif;
          font-weight: 500;
          border: 1px solid #1e1e1e;
          cursor: pointer;
          transition: all 0.3s;
          text-align: center;
        }
        .btn-secondary:hover { border-color: #555; color: #f0ebe3; }

        /* Hero right — editorial layout */
        .hero-right {
          display: grid;
          grid-template-rows: 1fr 1fr;
          border-left: 1px solid #1a1a1a;
        }

        .feature-block {
          padding: 3rem;
          border-bottom: 1px solid #1a1a1a;
          display: flex;
          flex-direction: column;
          justify-content: flex-end;
          position: relative;
          overflow: hidden;
        }
        .feature-block:last-child { border-bottom: none; }

        .feature-num {
          font-family: 'Playfair Display', serif;
          font-size: 5rem;
          font-weight: 900;
          color: #111;
          line-height: 1;
          position: absolute;
          top: 1.5rem;
          right: 2rem;
        }
        .feature-title {
          font-family: 'Playfair Display', serif;
          font-size: 1.3rem;
          font-weight: 700;
          color: #f0ebe3;
          margin-bottom: 0.5rem;
          position: relative;
          z-index: 1;
        }
        .feature-desc {
          font-size: 0.6rem;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: #444;
          line-height: 1.8;
          position: relative;
          z-index: 1;
        }
        .feature-line {
          width: 40px;
          height: 1px;
          background: #c9a84c;
          margin-bottom: 1.25rem;
          position: relative;
          z-index: 1;
        }

        /* Bottom strip */
        .bottom-strip {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          border-top: 1px solid #1a1a1a;
          position: relative;
          z-index: 10;
        }
        .strip-item {
          padding: 1.75rem 4rem;
          border-right: 1px solid #1a1a1a;
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .strip-item:last-child { border-right: none; }
        .strip-num {
          font-family: 'Playfair Display', serif;
          font-size: 1.5rem;
          font-weight: 900;
          color: #c9a84c;
        }
        .strip-label {
          font-size: 0.58rem;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          color: #444;
          line-height: 1.6;
        }

        /* Animations */
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .fade-1 { animation: fadeUp 0.8s ease forwards; }
        .fade-2 { animation: fadeUp 0.8s 0.15s ease forwards; opacity: 0; }
        .fade-3 { animation: fadeUp 0.8s 0.3s ease forwards; opacity: 0; }
        .fade-4 { animation: fadeUp 0.8s 0.45s ease forwards; opacity: 0; }
      `}</style>

      <div className="landing">
        <div className="gold-line" />

        {/* Header */}
        <header className="header fade-1">
          <div className="logo">AUR<span>A</span></div>
          <div className="header-tagline">AI — Wardrobe Intelligence Platform</div>
        </header>

        {/* Hero */}
        <main className="hero">
          <div className="hero-left fade-2">
            <div className="issue-tag">Fashion Intelligence</div>
            <h1 className="hero-title">
              Dress<br />with
              <em>Intent.</em>
            </h1>
            <p className="hero-body">
              AURA learns your wardrobe, understands colour harmony, and curates outfits worthy of your best self — powered by AI trained on fashion.
            </p>
            <div className="hero-actions">
              <button className="btn-primary" onClick={() => router.push('/register')}>
                Begin Your Collection
              </button>
              <button className="btn-secondary" onClick={() => router.push('/login')}>
                Sign In
              </button>
            </div>
          </div>

          <div className="hero-right fade-3">
            <div className="feature-block">
              <div className="feature-num">01</div>
              <div className="feature-line" />
              <div className="feature-title">AI Garment Detection</div>
              <div className="feature-desc">
                Upload any photo.<br />
                AURA identifies type,<br />
                colour & pattern instantly.
              </div>
            </div>
            <div className="feature-block">
              <div className="feature-num">02</div>
              <div className="feature-line" />
              <div className="feature-title">Outfit Curation</div>
              <div className="feature-desc">
                Smart pairings based on<br />
                colour theory & your<br />
                personal collection.
              </div>
            </div>
          </div>
        </main>

        {/* Stats strip */}
        <div className="bottom-strip fade-4">
          <div className="strip-item">
            <div className="strip-num">95%</div>
            <div className="strip-label">Garment<br />Detection Accuracy</div>
          </div>
          <div className="strip-item">
            <div className="strip-num">20+</div>
            <div className="strip-label">Colours<br />Recognised</div>
          </div>
          <div className="strip-item">
            <div className="strip-num">∞</div>
            <div className="strip-label">Outfit<br />Combinations</div>
          </div>
        </div>
      </div>
    </>
  );
}
