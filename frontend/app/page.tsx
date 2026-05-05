"use client";
import { useEffect, useState, useCallback, useRef } from "react";

const BASE = "/ChataBot";
const API = `${BASE}/api`;
const PASSWORD = "Dagulec";
const AUTH_KEY = "chatabot_auth";

function DogIcon({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      {/* Head */}
      <ellipse cx="12" cy="13" rx="7" ry="6.5" />
      {/* Left ear */}
      <path d="M5.5 9.5 C4 7 4.5 4 6.5 4 C8 4 8.5 6.5 8 9" />
      {/* Right ear */}
      <path d="M18.5 9.5 C20 7 19.5 4 17.5 4 C16 4 15.5 6.5 16 9" />
      {/* Nose */}
      <ellipse cx="12" cy="14.5" rx="2" ry="1.2" fill="white" stroke="none" />
      {/* Eyes */}
      <circle cx="9.5" cy="11.5" r="0.8" fill="white" stroke="none" />
      <circle cx="14.5" cy="11.5" r="0.8" fill="white" stroke="none" />
    </svg>
  );
}

function PasswordGate({ onUnlock }: { onUnlock: () => void }) {
  const [value, setValue] = useState("");
  const [error, setError] = useState(false);
  const [shake, setShake] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const submit = () => {
    if (value === PASSWORD) {
      localStorage.setItem(AUTH_KEY, "1");
      onUnlock();
    } else {
      setError(true);
      setShake(true);
      setValue("");
      setTimeout(() => setShake(false), 500);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className={`glass rounded-2xl p-8 w-full max-w-sm text-center ${shake ? "animate-[shake_0.4s_ease]" : ""}`}>
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto mb-6">
          <DogIcon size={28} />
        </div>
        <h1 className="text-xl font-semibold text-white mb-1">ChataBot</h1>
        <p className="text-sm text-gray-500 mb-6">Wprowadź hasło dostępu</p>
        <input
          ref={inputRef}
          type="password"
          value={value}
          onChange={e => { setValue(e.target.value); setError(false); }}
          onKeyDown={e => e.key === "Enter" && submit()}
          placeholder="Hasło"
          className={`w-full bg-white/5 border rounded-xl px-4 py-3 text-white placeholder-gray-600 text-center
            focus:outline-none focus:ring-2 transition-all mb-3
            ${error ? "border-red-500/60 focus:ring-red-500/30" : "border-white/10 focus:ring-indigo-500/40"}`}
        />
        {error && <p className="text-xs text-red-400 mb-3">Nieprawidłowe hasło</p>}
        <button
          onClick={submit}
          className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium transition-all"
        >
          Wejdź
        </button>
      </div>
      <style>{`
        @keyframes shake {
          0%,100% { transform: translateX(0); }
          20% { transform: translateX(-8px); }
          40% { transform: translateX(8px); }
          60% { transform: translateX(-6px); }
          80% { transform: translateX(6px); }
        }
      `}</style>
    </div>
  );
}

interface ScrapeResult {
  total: number;
  nearby: number;
  new: number;
}

function Toast({ data, onDone }: { data: ScrapeResult; onDone: () => void }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setVisible(false), 5000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 glass rounded-2xl px-6 py-4 shadow-2xl transition-all duration-700
        ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3 pointer-events-none"}`}
      onTransitionEnd={() => { if (!visible) onDone(); }}
    >
      <div className="text-sm font-semibold text-white mb-1">Skanowanie zakończone</div>
      <div className="text-xs text-gray-400 leading-relaxed">
        Znaleziono <span className="text-white font-medium">{data.total}</span> ogłoszeń łącznie
        <br />
        W zasięgu 20 km: <span className="text-indigo-300 font-medium">{data.nearby}</span>
        {data.new > 0 && (
          <> · <span className="text-green-400 font-medium">+{data.new} nowych</span></>
        )}
        {data.new === 0 && (
          <> · <span className="text-gray-500">brak nowych</span></>
        )}
      </div>
    </div>
  );
}

interface Listing {
  id: number;
  url: string;
  agency: string;
  title: string;
  location: string;
  price: number | null;
  area: number | null;
  distance_km: number | null;
  interested: number;
  found_at: string;
}

type SortKey = "found_at" | "price" | "area" | "distance_km" | "price_per_m2";
type SortDir = "asc" | "desc";

const fmtPrice = (p: number | null) =>
  p ? p.toLocaleString("pl-PL") + " zł" : "—";

const pricePerM2 = (l: Listing) =>
  l.price && l.area ? Math.round(l.price / l.area) : null;

const fmtDate = (s: string) => {
  const d = new Date(s.replace(" ", "T"));
  return d.toLocaleDateString("pl-PL", { day: "2-digit", month: "short", year: "numeric" });
};

const AGENCY_COLORS: Record<string, string> = {
  "SCN": "bg-violet-500/20 text-violet-300 border-violet-500/30",
  "Łowcy Nieruchomości": "bg-blue-500/20 text-blue-300 border-blue-500/30",
  "TRUhome": "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  "REMA": "bg-orange-500/20 text-orange-300 border-orange-500/30",
  "Realton": "bg-pink-500/20 text-pink-300 border-pink-500/30",
  "Kopalnia Nieruchomości": "bg-amber-500/20 text-amber-300 border-amber-500/30",
  "Indexo": "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
  "WGN Katowice": "bg-red-500/20 text-red-300 border-red-500/30",
};

const agencyColor = (a: string) =>
  AGENCY_COLORS[a] ?? "bg-gray-500/20 text-gray-300 border-gray-500/30";

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="glass rounded-2xl px-5 py-4">
      <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">{label}</div>
      <div className="text-2xl font-semibold text-white">{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-0.5">{sub}</div>}
    </div>
  );
}

function SortBtn({ col, label, sortKey, sortDir, onSort }: {
  col: SortKey; label: string; sortKey: SortKey; sortDir: SortDir;
  onSort: (k: SortKey) => void;
}) {
  const active = sortKey === col;
  return (
    <button
      onClick={() => onSort(col)}
      className={`flex items-center gap-1 text-xs uppercase tracking-wider font-medium transition-colors select-none
        ${active ? "text-indigo-400" : "text-gray-500 hover:text-gray-300"}`}
    >
      {label}
      <span className="text-[10px]">
        {active ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
      </span>
    </button>
  );
}

export default function Home() {
  const [auth, setAuth] = useState<boolean | null>(null);
  const [listings, setListings] = useState<Listing[]>([]);
  const [agencies, setAgencies] = useState<string[]>([]);
  const [selectedAgency, setSelectedAgency] = useState("");
  const [showInterested, setShowInterested] = useState(false);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("found_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [toast, setToast] = useState<ScrapeResult | null>(null);

  useEffect(() => {
    setAuth(localStorage.getItem(AUTH_KEY) === "1");
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const qs = selectedAgency ? `?agency=${encodeURIComponent(selectedAgency)}` : "";
      const [listRes, agRes] = await Promise.all([
        fetch(`${API}/listings${qs}`),
        fetch(`${API}/agencies`),
      ]);
      setListings(await listRes.json());
      setAgencies(await agRes.json());
      setLastRefresh(new Date());
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [selectedAgency]);

  useEffect(() => { load(); }, [load]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortDir(key === "found_at" ? "desc" : "asc"); }
  };

  const scrapeNow = async () => {
    setScraping(true);
    try {
      const res = await fetch(`${API}/scrape`, { method: "POST" });
      const data: ScrapeResult = await res.json();
      await load();
      setToast(data);
    } catch (e) {
      console.error(e);
    }
    setScraping(false);
  };

  const toggleInterest = async (id: number, current: number) => {
    const next = !current;
    await fetch(`${API}/listings/${id}/interest?interested=${next}`, { method: "PATCH" });
    setListings(prev => prev.map(l => l.id === id ? { ...l, interested: next ? 1 : 0 } : l));
  };

  const filtered = showInterested ? listings.filter(l => l.interested) : listings;
  const sorted = [...filtered].sort((a, b) => {
    let av: number | null, bv: number | null;
    if (sortKey === "price_per_m2") { av = pricePerM2(a); bv = pricePerM2(b); }
    else if (sortKey === "found_at") { av = new Date(a.found_at).getTime(); bv = new Date(b.found_at).getTime(); }
    else { av = a[sortKey]; bv = b[sortKey]; }
    if (av == null) return 1; if (bv == null) return -1;
    return sortDir === "asc" ? av - bv : bv - av;
  });

  const interested = listings.filter(l => l.interested);
  const avgPrice = listings.filter(l => l.price).reduce((s, l) => s + l.price!, 0) / (listings.filter(l => l.price).length || 1);

  if (auth === null) return null; // hydration guard
  if (!auth) return <PasswordGate onUnlock={() => setAuth(true)} />;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0f1117]/80 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <DogIcon size={18} />
            </div>
            <div>
              <span className="font-semibold text-white">ChataBot</span>
              <span className="text-gray-500 text-sm ml-2">Katowice ±20 km</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {lastRefresh && (
              <span className="text-xs text-gray-600 hidden sm:block">
                {lastRefresh.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })}
              </span>
            )}
            <button
              onClick={scrapeNow}
              disabled={loading || scraping}
              className="px-4 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-2"
            >
              <span className={`inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full ${scraping || loading ? "animate-spin" : "hidden"}`} />
              {scraping ? "Skanuję…" : "Odśwież"}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          <StatCard label="Ogłoszenia" value={listings.length} sub="spełniające kryteria" />
          <StatCard label="Zainteresowane" value={interested.length} sub={interested.length ? "zaznaczone" : "brak"} />
          <StatCard
            label="Śr. cena"
            value={listings.length ? Math.round(avgPrice / 1000) + " tys." : "—"}
            sub="zł"
          />
          <StatCard label="Agencje" value={agencies.length} sub="aktywnych" />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mb-6">
          <div className="relative">
            <select
              className="glass rounded-xl px-4 py-2.5 text-sm text-gray-200 bg-transparent appearance-none pr-8 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 cursor-pointer"
              value={selectedAgency}
              onChange={e => setSelectedAgency(e.target.value)}
            >
              <option value="" className="bg-[#1a1d27]">Wszystkie agencje</option>
              {agencies.map(a => <option key={a} value={a} className="bg-[#1a1d27]">{a}</option>)}
            </select>
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none text-xs">▾</span>
          </div>

          <button
            onClick={() => setShowInterested(s => !s)}
            className={`px-4 py-2.5 rounded-xl text-sm font-medium border transition-all
              ${showInterested
                ? "bg-green-500/20 border-green-500/40 text-green-300"
                : "glass text-gray-400 hover:text-gray-200"}`}
          >
            ★ Zainteresowane
            {interested.length > 0 && (
              <span className="ml-2 px-1.5 py-0.5 bg-green-500/30 rounded-md text-xs text-green-300">
                {interested.length}
              </span>
            )}
          </button>

          <div className="ml-auto flex items-center gap-2 text-sm text-gray-500">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse inline-block" />
            {sorted.length} wyników
          </div>
        </div>

        {/* Table */}
        {loading && (
          <div className="glass rounded-2xl p-16 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-400 rounded-full animate-spin" />
              <span className="text-sm text-gray-500">Ładowanie ofert…</span>
            </div>
          </div>
        )}

        {!loading && sorted.length === 0 && (
          <div className="glass rounded-2xl p-16 text-center text-gray-500">
            Brak ogłoszeń spełniających kryteria.
          </div>
        )}

        {!loading && sorted.length > 0 && (
          <div className="glass rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="px-5 py-3.5 text-left w-10"></th>
                    <th className="px-5 py-3.5 text-left text-xs text-gray-500 uppercase tracking-wider font-medium">Agencja</th>
                    <th className="px-5 py-3.5 text-left text-xs text-gray-500 uppercase tracking-wider font-medium">Oferta</th>
                    <th className="px-5 py-3.5 text-left">
                      <SortBtn col="area" label="Pow." sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                    </th>
                    <th className="px-5 py-3.5 text-left">
                      <SortBtn col="price" label="Cena" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                    </th>
                    <th className="px-5 py-3.5 text-left hidden md:table-cell">
                      <SortBtn col="price_per_m2" label="zł/m²" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                    </th>
                    <th className="px-5 py-3.5 text-left hidden sm:table-cell">
                      <SortBtn col="distance_km" label="Odl." sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                    </th>
                    <th className="px-5 py-3.5 text-left hidden lg:table-cell">
                      <SortBtn col="found_at" label="Data" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04]">
                  {sorted.map((l) => {
                    const ppm = pricePerM2(l);
                    return (
                      <tr
                        key={l.id}
                        className={`group transition-colors
                          ${l.interested
                            ? "bg-green-500/5 hover:bg-green-500/10"
                            : "hover:bg-white/[0.03]"}`}
                      >
                        <td className="px-5 py-4">
                          <button
                            onClick={() => toggleInterest(l.id, l.interested)}
                            className={`text-lg transition-all hover:scale-110 active:scale-95
                              ${l.interested ? "opacity-100" : "opacity-20 hover:opacity-60"}`}
                            title="Zainteresowany"
                          >
                            ★
                          </button>
                        </td>
                        <td className="px-5 py-4">
                          <span className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${agencyColor(l.agency)}`}>
                            {l.agency}
                          </span>
                        </td>
                        <td className="px-5 py-4 max-w-xs">
                          <a
                            href={l.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-gray-200 hover:text-white hover:underline underline-offset-2 font-medium line-clamp-1"
                          >
                            {l.title || "Ogłoszenie"}
                          </a>
                          <div className="text-xs text-gray-600 mt-0.5 sm:hidden">
                            {l.distance_km != null ? `${l.distance_km.toFixed(1)} km` : ""}{" "}
                            {l.location}
                          </div>
                          <div className="text-xs text-gray-600 mt-0.5 hidden sm:block">
                            {l.location}
                          </div>
                        </td>
                        <td className="px-5 py-4 whitespace-nowrap">
                          <span className="text-sm font-semibold text-white">
                            {l.area ? `${l.area} m²` : "—"}
                          </span>
                        </td>
                        <td className="px-5 py-4 whitespace-nowrap">
                          <span className="text-sm font-semibold text-white">
                            {l.price ? (l.price / 1000).toFixed(0) + "k" : "—"}
                          </span>
                          <span className="text-xs text-gray-500 ml-1">zł</span>
                        </td>
                        <td className="px-5 py-4 whitespace-nowrap hidden md:table-cell">
                          {ppm ? (
                            <span className="text-sm text-gray-300">
                              {ppm.toLocaleString("pl-PL")}
                              <span className="text-xs text-gray-600 ml-1">zł</span>
                            </span>
                          ) : "—"}
                        </td>
                        <td className="px-5 py-4 whitespace-nowrap hidden sm:table-cell">
                          {l.distance_km != null ? (
                            <div className="flex items-center gap-2">
                              <div className="w-12 h-1 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-indigo-500 rounded-full"
                                  style={{ width: `${Math.min(100, (l.distance_km / 20) * 100)}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-400">{l.distance_km.toFixed(1)} km</span>
                            </div>
                          ) : "—"}
                        </td>
                        <td className="px-5 py-4 whitespace-nowrap hidden lg:table-cell">
                          <span className="text-xs text-gray-500">{fmtDate(l.found_at)}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <footer className="mt-8 text-center text-xs text-gray-700">
          Filtr: sprzedaż · dom · 100–180 m² · ≤20 km od Katowic · aktualizacja co godzinę
        </footer>
      </main>

      {toast && <Toast data={toast} onDone={() => setToast(null)} />}
    </div>
  );
}
