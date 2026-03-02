"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import axios from "axios";
import "./dashboard.css";

const API_URL = "https://aura-v2-vhvv.onrender.com";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, token, user, logout } = useAuthStore();
  const [itemCount, setItemCount] = useState(0);
  const [recentItems, setRecentItems] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    axios.get(`${API_URL}/api/wardrobe/items`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => {
      setItemCount(r.data.length);
      setRecentItems(r.data.slice(0, 4));
    }).catch(() => {});
  }, [isAuthenticated]);

  const handleLogout = () => { logout(); router.push("/login"); };

  if (!isAuthenticated) return null;

  return (
    <div className="dashboard">
      <header className="header">
        <div className="logo">AUR<span>A</span></div>
        <nav className="nav">
          <a onClick={() => router.push("/wardrobe")}>Wardrobe</a>
          <a onClick={() => router.push("/recommendations")}>Looks</a>
          <button className="nav-logout" onClick={handleLogout}>Exit</button>
        </nav>
      </header>

      <section className="hero fade-up">
        <div className="hero-left">
          <div className="hero-issue">Your Personal Edition</div>
          <h1 className="hero-title">
            Your<br /><em>Style,</em><br />Curated.
          </h1>
          <p className="hero-subtitle">
            Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}. Your wardrobe awaits — dressed for the life you want to live.
          </p>
        </div>
        <div className="hero-right">
          <div className="stat-block">
            <div className="stat-number">{itemCount}</div>
            <div className="stat-label">Pieces in Collection</div>
          </div>
          <div className="hero-divider" />
        </div>
      </section>

      <section className="actions fade-up-2">
        <div className="action-card" onClick={() => router.push("/wardrobe")}>
          <div className="action-number">01</div>
          <div className="action-title">My Wardrobe</div>
          <div className="action-desc">Browse &amp; manage<br />your collection</div>
          <div className="action-arrow">↗</div>
        </div>
        <div className="action-card" onClick={() => router.push("/wardrobe")}>
          <div className="action-number">02</div>
          <div className="action-title">Add Pieces</div>
          <div className="action-desc">Upload new items<br />for AI detection</div>
          <div className="action-arrow">↗</div>
        </div>
        <div className="action-card" onClick={() => router.push("/recommendations")}>
          <div className="action-number">03</div>
          <div className="action-title">Today&apos;s Look</div>
          <div className="action-desc">AI outfit pairings<br />curated for you</div>
          <div className="action-arrow">↗</div>
        </div>
      </section>

      <section className="recent fade-up-3">
        <div className="section-header">
          <div className="section-title">Recently Added</div>
          <button className="section-link" onClick={() => router.push("/wardrobe")}>View All →</button>
        </div>
        <div className="recent-grid">
          {recentItems.length === 0 ? (
            <div className="empty-recent">Your collection is empty — begin by uploading your first piece.</div>
          ) : recentItems.map((item) => (
            <div className="recent-item" key={item.id}>
              <img src={`${API_URL}${item.image_url}`} alt={item.garment_type} className="recent-img" />
              <div className="recent-info">
                <div className="recent-type">{item.garment_type}</div>
                <div className="recent-color">{item.color_description || item.color}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="footer-strip">
        <div className="footer-copy">© 2024 Aura — AI Wardrobe</div>
        <div className="footer-copy">Fashion Intelligence Platform</div>
      </div>
    </div>
  );
}
