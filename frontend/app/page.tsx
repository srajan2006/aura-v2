'use client';

import { useRouter } from 'next/navigation';
import './landing.css';

export default function Home() {
  const router = useRouter();

  return (
    <div className="landing">
      <div className="gold-line" />

      <header className="header fade-1">
        <div className="logo">AUR<span>A</span></div>
        <div className="header-tagline">AI — Wardrobe Intelligence Platform</div>
      </header>

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
              colour &amp; pattern instantly.
            </div>
          </div>
          <div className="feature-block">
            <div className="feature-num">02</div>
            <div className="feature-line" />
            <div className="feature-title">Outfit Curation</div>
            <div className="feature-desc">
              Smart pairings based on<br />
              colour theory &amp; your<br />
              personal collection.
            </div>
          </div>
        </div>
      </main>

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
          <div className="strip-num">&#8734;</div>
          <div className="strip-label">Outfit<br />Combinations</div>
        </div>
      </div>
    </div>
  );
}
