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

function fmt_price(p: number | null) {
  if (!p) return "—";
  return p.toLocaleString("pl-PL") + " zł";
}

export default function Home() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [agencies, setAgencies] = useState<string[]>([]);
  const [selectedAgency, setSelectedAgency] = useState<string>("");
  const [showInterested, setShowInterested] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const qs = selectedAgency ? `?agency=${encodeURIComponent(selectedAgency)}` : "";
    const [listRes, agRes] = await Promise.all([
      fetch(`${API}/listings${qs}`),
      fetch(`${API}/agencies`),
    ]);
    setListings(await listRes.json());
    setAgencies(await agRes.json());
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

  const visible = showInterested ? listings.filter((l) => l.interested) : listings;

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">🏠 Ogłoszenia – domy w Katowicach ±15km</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6 items-center">
        <select
          className="border rounded px-3 py-2 text-sm"
          value={selectedAgency}
          onChange={(e) => setSelectedAgency(e.target.value)}
        >
          <option value="">Wszystkie agencje</option>
          {agencies.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>

        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={showInterested}
            onChange={(e) => setShowInterested(e.target.checked)}
            className="w-4 h-4"
          />
          Tylko zainteresowane
        </label>

        <span className="text-sm text-gray-500 ml-auto">
          {visible.length} ogłoszeń
        </span>
      </div>

      {loading && <p className="text-gray-500">Ładowanie…</p>}

      {!loading && visible.length === 0 && (
        <p className="text-gray-500 text-center py-12">Brak ogłoszeń spełniających kryteria.</p>
      )}

      {/* Table */}
      {!loading && visible.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 text-left">
              <tr>
                <th className="px-3 py-2">Zainteresowany</th>
                <th className="px-3 py-2">Agencja</th>
                <th className="px-3 py-2">Tytuł</th>
                <th className="px-3 py-2">Lokalizacja</th>
                <th className="px-3 py-2">Pow.</th>
                <th className="px-3 py-2">Cena</th>
                <th className="px-3 py-2">Odl.</th>
                <th className="px-3 py-2">Data</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((l) => (
                <tr
                  key={l.id}
                  className={`border-t hover:bg-gray-50 ${l.interested ? "bg-green-50" : ""}`}
                >
                  <td className="px-3 py-2 text-center">
                    <input
                      type="checkbox"
                      checked={l.interested === 1}
                      onChange={() => toggleInterest(l.id, l.interested)}
                      className="w-4 h-4 cursor-pointer"
                    />
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap font-medium">{l.agency}</td>
                  <td className="px-3 py-2">
                    <a
                      href={l.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {l.title || "Ogłoszenie"}
                    </a>
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap">{l.location}</td>
                  <td className="px-3 py-2 whitespace-nowrap">
                    {l.area ? `${l.area} m²` : "—"}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap">{fmt_price(l.price)}</td>
                  <td className="px-3 py-2 whitespace-nowrap">
                    {l.distance_km ? `${l.distance_km.toFixed(1)} km` : "—"}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-gray-400 text-xs">
                    {l.found_at?.slice(0, 16)}
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
