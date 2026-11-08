import "./globals.css";
import Nav from "./components/Nav";

export const metadata = {
  title: "Pulse — Cross-Cloud Streaming Analytics",
  description:
    "Real-time analytics over a Kafka stream, reconciled exactly-once across AWS and Azure.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Nav />
        {children}
      </body>
    </html>
  );
}
