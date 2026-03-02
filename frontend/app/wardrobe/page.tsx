"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import axios from "axios";
import "./wardrobe.css";

const API_URL = "http://localhost:8000";
const GARMENT_TYPES = ["tshirt", "shirt", "jacket", "jeans"];
const COLORS = ["black","darkgrey","grey","lightgrey","white","red","orange","yellow","green","lightgreen","blue","lightblue","skyblue","navy","purple","pink","brown","tan","beige","khaki","cream"];
const PATTERNS = ["solid", "striped", "checked", "printed"];

interface WardrobeItem {
  id: string; garment_type: string; color: string;
  is_multicolor?: boolean; pattern?: string;
  color_description?: string; full_description?: string; image_url: string;
}

export default function WardrobePage() {
  const router = useRouter();
  const { isAuthenticated, token } = useAuthStore();
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [editingItem, setEditingItem] = useState<WardrobeItem | null>(null);
  const [editState, setEditState] = useState({ garment_type: "", color: "", pattern: "solid", is_multicolor: false });
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    fetchItems();
  }, [isAuthenticated]);

  const fetchItems = async () => {
    try {
      const r = await axios.get(`${API_URL}/api/wardrobe/items`, { headers: { Authorization: `Bearer ${token}` } });
      setItems(r.data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; if (!file) return;
    setUploading(true);
    const fd = new FormData(); fd.append("file", file);
    try {
      await axios.post(`${API_URL}/api/wardrobe/upload`, fd, {
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" }
      });
      fetchItems();
    } catch { alert("Upload failed"); } finally { setUploading(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this piece from your collection?")) return;
    await axios.delete(`${API_URL}/api/wardrobe/items/${id}`, { headers: { Authorization: `Bearer ${token}` } });
    fetchItems();
  };

  const openEdit = (item: WardrobeItem) => {
    setEditingItem(item);
    setEditState({ garment_type: item.garment_type, color: item.color, pattern: item.pattern || "solid", is_multicolor: item.is_multicolor || false });
  };

  const handleSave = async () => {
    if (!editingItem) return; setSaving(true);
    try {
      await axios.patch(`${API_URL}/api/wardrobe/items/${editingItem.id}`, {
        ...editState,
        color_description: editState.is_multicolor ? `multicolor-${editState.color}` : editState.color,
        full_description: `${editState.pattern} ${editState.color} ${editState.garment_type}`,
      }, { headers: { Authorization: `Bearer ${token}` } });
      setEditingItem(null); fetchItems();
    } catch { alert("Save failed"); } finally { setSaving(false); }
  };

  const filtered = filter === "all" ? items : items.filter(i => i.garment_type === filter);

  if (!isAuthenticated) return null;

  return (
    <div className="page">
      <header className="header">
        <div className="logo">AUR<span>A</span></div>
        <nav className="nav">
          <a onClick={() => router.push("/dashboard")}>Home</a>
          <a className="active">Wardrobe</a>
          <a onClick={() => router.push("/recommendations")}>Looks</a>
        </nav>
      </header>

      <div className="page-head fade-up">
        <h1 className="page-title">My<br /><em>Collection</em></h1>
        <div className="page-count">{items.length} {items.length === 1 ? "piece" : "pieces"}</div>
      </div>

      <div className="toolbar">
        <div className="filters">
          {["all", "tshirt", "shirt", "jacket", "jeans"].map(f => (
            <button key={f} className={`filter-btn ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
              {f === "all" ? "All" : f}
            </button>
          ))}
        </div>
        <label className="upload-btn">
          {uploading ? "Uploading..." : "+ Add Piece"}
          <input type="file" accept="image/*" onChange={handleUpload} style={{ display: "none" }} disabled={uploading} />
        </label>
      </div>

      <div className="grid">
        {loading ? (
          <div className="empty"><div className="empty-title">Loading collection...</div></div>
        ) : filtered.length === 0 ? (
          <div className="empty">
            <div className="empty-title">Nothing here yet.</div>
            <div className="empty-sub">Upload your first piece to begin</div>
          </div>
        ) : filtered.map(item => (
          <div className="item" key={item.id}>
            <img src={`${API_URL}${item.image_url}`} alt={item.garment_type} className="item-img" />
            <div className="item-overlay">
              <div className="overlay-actions">
                <button className="ov-btn ov-edit" onClick={() => openEdit(item)}>Edit</button>
                <button className="ov-btn ov-del" style={{ border: "1px solid #555" }} onClick={() => handleDelete(item.id)}>Remove</button>
              </div>
            </div>
            <div className="item-info">
              <div className="item-type">{item.garment_type}</div>
              <div className="item-meta">{item.pattern && item.pattern !== "solid" ? `${item.pattern} · ` : ""}{item.color_description || item.color}</div>
              {item.pattern && item.pattern !== "solid" && <span className="item-badge">{item.pattern}</span>}
            </div>
          </div>
        ))}
      </div>

      {editingItem && (
        <div className="modal-bg" onClick={e => e.target === e.currentTarget && setEditingItem(null)}>
          <div className="modal">
            <div className="modal-header">
              <div className="modal-title">Edit Piece</div>
              <button className="modal-close" onClick={() => setEditingItem(null)}>x</button>
            </div>
            <img src={`${API_URL}${editingItem.image_url}`} alt="" className="modal-img" />
            <div className="modal-body">
              <div className="modal-section">
                <div className="modal-label">Garment Type</div>
                <div className="btn-group">
                  {GARMENT_TYPES.map(t => (
                    <button key={t} className={`choice-btn ${editState.garment_type === t ? "selected" : ""}`} onClick={() => setEditState({ ...editState, garment_type: t })}>{t}</button>
                  ))}
                </div>
              </div>
              <div className="modal-section">
                <div className="modal-label">Pattern</div>
                <div className="btn-group">
                  {PATTERNS.map(p => (
                    <button key={p} className={`choice-btn ${editState.pattern === p ? "selected" : ""}`} onClick={() => setEditState({ ...editState, pattern: p })}>{p}</button>
                  ))}
                </div>
              </div>
              <div className="modal-section">
                <div className="modal-label">Color</div>
                <div className="btn-group">
                  {COLORS.map(c => (
                    <button key={c} className={`choice-btn ${editState.color === c ? "selected" : ""}`} onClick={() => setEditState({ ...editState, color: c })}>{c}</button>
                  ))}
                </div>
              </div>
              <div className="modal-section">
                <div className="modal-label">Options</div>
                <div className="toggle-row">
                  <input type="checkbox" id="mc" checked={editState.is_multicolor} onChange={e => setEditState({ ...editState, is_multicolor: e.target.checked })} />
                  <label htmlFor="mc" className="toggle-label">Multicolor</label>
                </div>
              </div>
              <div className="preview-box">
                Preview: <strong>{editState.pattern !== "solid" ? `${editState.pattern} ` : ""}{editState.is_multicolor ? `multicolor-${editState.color}` : editState.color} {editState.garment_type}</strong>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-cancel" onClick={() => setEditingItem(null)}>Cancel</button>
              <button className="btn-save" onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}