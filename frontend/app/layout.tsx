import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChataBot – Domy Katowice",
  description: "Monitoring ofert domów w Katowicach i okolicach",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pl" className="dark">
      <body className="bg-[#0f1117] text-gray-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
