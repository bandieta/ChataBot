"use client";
import { useEffect, useState, useCallback } from "react";

const API = "/api";

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

function fmt_price(p: number | null) {
  if (!p) return "—";
  return p.toLocaleString("pl-PL") + " zł";
}

function price_per_m2(l: Listing): number | null {
  if (!l.price || !l.area) return null;
  return Math.round(l.price / l.area);
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <span className="text-gray-300 ml-1">↕</span>;
  return <span className="text-blue-600 ml-1">{dir === "asc" ? "↑" : "↓"}</span>;
}

export default function Home() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [agencies, setAgencies] = useState<string[]>([]);
  const [selectedAgency, setSelectedAgency] = useState<string>("");
  const [showInterested, setShowInterested] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("found_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const qs = selectedAgency ? `?agency=${encodeURIComponent(selectedAgency)}` : "";
    const [listRes, agRes] = await Promise.all([
      fetch(`${API}/listings${qs}`),
      fetch(`${API}/agencies`),
    ]);
    setListings(await listRes.json());
    setAgencies(await agRes.json());
    setLastRefresh(new Date());
    setLoading(false);
  }, [selectedAgency]);

  useEffect(() => { load(); }, [load]);

  const toggleInterest = async (id: number, current: number) => {
    const next = current === 0;
    await fetch(`${API}/listings/${id}/interest?interested=${next}`, { method: "PATCH" });
    setListings((prev) =>
      prev.map((l) => (l.id === id ? { ...l, interested: next ? 1 : 0 } : l))
    );
  };

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "found_at" ? "desc" : "asc");
    }
  };

  const filtered = showInterested ? listings.filter((l) => l.interested) : listings;

  const sorted = [...filtered].sort((a, b) => {
    let av: number | null, bv: number | null;
    if (sortKey === "price_per_m2") {
      av = price_per_m2(a);
      bv = price_per_m2(b);
    } else if (sortKey === "found_at") {
      av = new Date(a.found_at).getTime();
      bv = new Date(b.found_at).getTime();
    } else {
      av = a[sortKey];
      bv = b[sortKey];
    }
    if (av === null) return 1;
    if (bv === null) return -1;
    return sortDir === "asc" ? av - bv : bv - av;
  });

  const interestedCount = listings.filter((l) => l.interested).length;

  const Th = ({ label, sk }: { label: string; sk: SortKey }) => (
    <th
      className="px-3 py-2 cursor-pointer select-none hover:bg-gray-200 whitespace-nowrap"
      onClick={() => handleSort(sk)}
    >
      {label}
      <SortIcon active={sortKey === sk} dir={sortDir} />
    </th>
  );

  return (
    <main className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold">Domy w Katowicach ±15 km</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            100–180 m² · sprzedaż · {listings.length} ogłoszeń
            {interestedCount > 0 && ` · ${interestedCount} zainteresowanych`}
          </p>
        </div>
        <button
          onClick={load}
          className="text-sm px-3 py-1.5 rounded border border-gray-300 hover:bg-gray-50 active:bg-gray-100"
          disabled={loading}
        >
          {loading ? "…" : "Odśwież"}
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4 items-center">
        <select
          className="border rounded px-3 py-1.5 text-sm bg-white"
          value={selectedAgency}
          onChange={(e) => setSelectedAgency(e.target.value)}
        >
          <option value="">Wszystkie agencje ({agencies.length})</option>
          {agencies.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>

        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={showInterested}
            onChange={(e) => setShowInterested(e.target.checked)}
            className="w-4 h-4 accent-green-600"
          />
          Tylko zainteresowane
        </label>

        {lastRefresh && (
          <span className="text-xs text-gray-400 ml-auto">
            Odświeżono: {lastRefresh.toLocaleTimeString("pl-PL")}
          </span>
        )}
      </div>

      {loading && (
        <div className="text-center py-16 text-gray-400">Ładowanie…</div>
      )}

      {!loading && sorted.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          Brak ogłoszeń spełniających kryteria.
        </div>
      )}

      {!loading && sorted.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 text-left text-xs uppercase tracking-wide text-gray-600">
              <tr>
                <th className="px-3 py-2 w-8"></th>
                <th className="px-3 py-2">Agencja</th>
                <th className="px-3 py-2">Tytuł</th>
                <th className="px-3 py-2">Lokalizacja</th>
                <Th label="Pow." sk="area" />
                <Th label="Cena" sk="price" />
                <Th label="zł/m²" sk="price_per_m2" />
                <Th label="Odl." sk="distance_km" />
                <Th label="Data" sk="found_at" />
              </tr>
            </thead>
            <tbody>
              {sorted.map((l) => (
                <tr
                  key={l.id}
                  className={`border-t transition-colors hover:bg-gray-50 ${
                    l.interested ? "bg-green-50 hover:bg-green-100" : ""
                  }`}
                >
                  <td className="px-3 py-2 text-center">
                    <input
                      type="checkbox"
                      checked={l.interested === 1}
                      onChange={() => toggleInterest(l.id, l.interested)}
                      className="w-4 h-4 cursor-pointer accent-green-600"
                      title="Zainteresowany"
                    />
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-xs font-medium text-gray-600">
                    {l.agency}
                  </td>
                  <td className="px-3 py-2 max-w-xs">
                    <a
                      href={l.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline line-clamp-2"
                    >
                      {l.title || "Ogłoszenie"}
                    </a>
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-600">
                    {l.location}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap font-medium">
                    {l.area ? `${l.area} m²` : "—"}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap font-medium">
                    {fmt_price(l.price)}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-gray-500">
                    {price_per_m2(l) ? `${price_per_m2(l)?.toLocaleString("pl-PL")} zł` : "—"}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                    {l.distance_km != null ? `${l.distance_km.toFixed(1)} km` : "—"}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-400">
                    {l.found_at?.slice(0, 16).replace("T", " ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
