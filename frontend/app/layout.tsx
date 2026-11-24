import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Banking Fraud & AML Intelligence",
  description: "Investigator workspace for fraud-risk and AML intelligence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
