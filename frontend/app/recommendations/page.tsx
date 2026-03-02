"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import axios from "axios";
import "./recommendations.css";

const API_URL = "http://localhost:8000";

interface OutfitItem {
  id: string; garment_type: string; color: string;
  pattern?: string; color_description?: string; image_url: string;
}

interface Outfit {
  occasion: string; items: OutfitItem[];
  score?: number; description?: string;
}

export default function RecommendationsPage() {
  const router = useRouter();
  const { isAuthenticated, token } = useAuthStore();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [selected, setSelected] = useState<Outfit | null>(null);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    fetchRecs();
  }, [isAuthenticated]);

  const fetchRecs = async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API_URL}/api/recommendations?refresh=true`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOutfits(r.data.outfits || []);
      setMessage(r.data.message || "");
    } catch {
      setMessage("Could not load recommendations.");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="page">
      <header className="header">
        <div className="logo">AUR<span>A</span></div>
        <nav className="nav">
          <a onClick={() => router.push("/dashboard")}>Home</a>
          <a onClick={() => router.push("/wardrobe")}>Wardrobe</a>
          <a className="active">Looks</a>
        </nav>
      </header>

      <div className="hero fade-up">
        <div>
          <h1 className="hero-title">Today&apos;s<br /><em>Looks</em></h1>
        </div>
        <div className="hero-right">
          <button className="refresh-btn" onClick={fetchRecs} disabled={loading}>
            {loading ? "Curating..." : "↺ Refresh Looks"}
          </button>
          <div className="hero-sub">
            {outfits.length > 0 ? `${outfits.length} outfits curated` : ""}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="loading-text">Curating your looks...</div>
          <div className="loading-dots">
            <div className="dot" />
            <div className="dot" />
            <div className="dot" />
          </div>
        </div>
      ) : outfits.length === 0 ? (
        <div className="empty">
          <div className="empty-title">No looks yet.</div>
          <div className="empty-msg">
            {message || "Add tops and bottoms to your wardrobe to unlock outfit suggestions."}
          </div>
          <button className="empty-btn" onClick={() => router.push("/wardrobe")}>
            Go to Wardrobe →
          </button>
        </div>
      ) : (
        <div className="outfits fade-up-2">
          <div className="outfit-count">
            {outfits.length} outfit{outfits.length !== 1 ? "s" : ""} curated from your collection
          </div>
          <div className="outfits-grid">
            {outfits.map((outfit, i) => {
              const cnt = Math.min(outfit.items.length, 3);
              return (
                <div className="outfit-card" key={i} onClick={() => setSelected(outfit)}>
                  <div className={`outfit-images count-${cnt}`}>
                    {outfit.items.slice(0, 3).map((item, j) => (
                      <img
                        key={j}
                        src={`${API_URL}${item.image_url}`}
                        alt={item.garment_type}
                        className="outfit-img"
                      />
                    ))}
                  </div>
                  <div className="outfit-info">
                    <div className="outfit-occasion">{outfit.occasion}</div>
                    <div className="outfit-name">
                      Look {i + 1}
                      <span className="outfit-arrow">↗</span>
                    </div>
                    <div className="outfit-pieces">
                      {outfit.items.map(it => it.garment_type).join(" · ")}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selected && (
        <div className="modal-bg" onClick={e => e.target === e.currentTarget && setSelected(null)}>
          <div className="modal">
            <div className="modal-header">
              <div>
                <div className="modal-occasion">{selected.occasion}</div>
                <div className="modal-title">Complete Look</div>
              </div>
              <button className="modal-close" onClick={() => setSelected(null)}>×</button>
            </div>
            <div className="modal-items">
              {selected.items.map((item, i) => (
                <div className="modal-item" key={i}>
                  <img
                    src={`${API_URL}${item.image_url}`}
                    alt={item.garment_type}
                    className="modal-item-img"
                  />
                  <div className="modal-item-info">
                    <div className="modal-item-type">{item.garment_type}</div>
                    <div className="modal-item-color">{item.color_description || item.color}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="modal-footer">
              <button className="modal-btn modal-btn-close" onClick={() => setSelected(null)}>
                Close
              </button>
              <button className="modal-btn modal-btn-wardrobe" onClick={() => router.push("/wardrobe")}>
                View Wardrobe
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}