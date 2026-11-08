// Official-style service marks, faithful to AWS Architecture Icons and
// Microsoft Azure service tiles (the square gradient logos), plus Apache Kafka
// (Simple Icons). Rendered inline as SVG so they're crisp and never 404.

export function KafkaIcon({ size = 28 }) {
  // Apache Kafka mark (Simple Icons path)
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="#231F20">
      <rect width="24" height="24" rx="5" fill="#ffffff" />
      <path transform="translate(4 3) scale(0.66)" fill="#231F20"
        d="M9.37 8.16a2.6 2.6 0 0 0-1.86.78V6.52a2.9 2.9 0 1 0-1.3 0v10.96a2.9 2.9 0 1 0 1.3 0v-1.37c.5.48 1.17.78 1.86.78a2.74 2.74 0 0 0 0-5.48 2.6 2.6 0 0 0-1.86.78V9.53c.5.48 1.17.79 1.86.79a2.74 2.74 0 1 0 0-5.49zm0 1.17a1.57 1.57 0 1 1 0 3.14 1.57 1.57 0 0 1 0-3.14zm-2.5 10.7a1.6 1.6 0 1 1-.01-3.2 1.6 1.6 0 0 1 0 3.2zm0-16.46a1.6 1.6 0 1 1 0 3.2 1.6 1.6 0 0 1 0-3.2zm2.5 12.3a1.57 1.57 0 1 1 0-3.13 1.57 1.57 0 0 1 0 3.14z" />
    </svg>
  );
}

export function S3Icon({ size = 28 }) {
  // AWS Simple Storage Service — the green bucket tile
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <defs>
        <linearGradient id="s3g" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stopColor="#1B660F" />
          <stop offset="1" stopColor="#6CAE3E" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="7" fill="url(#s3g)" />
      <path fill="#fff" d="M24 11c-5 0-9 1.3-9 3v20c0 1.7 4 3 9 3s9-1.3 9-3V14c0-1.7-4-3-9-3zm0 2c4.5 0 7 1.1 7 1.6s-2.5 1.6-7 1.6-7-1.1-7-1.6S19.5 13 24 13zm7 20.9c0 .5-2.5 1.6-7 1.6s-7-1.1-7-1.6v-3.3c1.7.9 4.3 1.3 7 1.3s5.3-.4 7-1.3zm0-6.5c0 .5-2.5 1.6-7 1.6s-7-1.1-7-1.6v-3.3c1.7.9 4.3 1.3 7 1.3s5.3-.4 7-1.3z" />
    </svg>
  );
}

export function DynamoIcon({ size = 28 }) {
  // AWS DynamoDB — the blue database tile
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <defs>
        <linearGradient id="ddbg" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stopColor="#2E27AD" />
          <stop offset="1" stopColor="#527FFF" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="7" fill="url(#ddbg)" />
      <path fill="#fff" d="M24 10c-6 0-11 1.6-11 3.6v20.8c0 2 5 3.6 11 3.6s11-1.6 11-3.6V13.6C35 11.6 30 10 24 10zm9 24.4c0 .9-3.4 2.2-9 2.2s-9-1.3-9-2.2v-4.6c2.1 1.2 5.4 1.8 9 1.8s6.9-.6 9-1.8zm0-7c0 .9-3.4 2.2-9 2.2s-9-1.3-9-2.2v-4.6c2.1 1.2 5.4 1.8 9 1.8s6.9-.6 9-1.8zm-9-5.2c-5.6 0-9-1.3-9-2.2s3.4-2.2 9-2.2 9 1.3 9 2.2-3.4 2.2-9 2.2z" />
    </svg>
  );
}

export function CosmosIcon({ size = 28 }) {
  // Azure Cosmos DB — the blue planet/orbit tile
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <defs>
        <linearGradient id="cosg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#5EA0EF" />
          <stop offset="1" stopColor="#0078D4" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="7" fill="url(#cosg)" />
      <circle cx="24" cy="24" r="9.5" fill="none" stroke="#fff" strokeWidth="1.8" />
      <ellipse cx="24" cy="24" rx="12.5" ry="5" fill="none" stroke="#fff" strokeWidth="1.5" transform="rotate(-25 24 24)" />
      <circle cx="33" cy="17.5" r="1.7" fill="#fff" />
    </svg>
  );
}

export function LakeIcon({ size = 28 }) {
  // Azure Data Lake Storage (ADLS Gen2) — blue storage tile
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <defs>
        <linearGradient id="adlsg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#5EA0EF" />
          <stop offset="1" stopColor="#0078D4" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="7" fill="url(#adlsg)" />
      <ellipse cx="24" cy="16" rx="9" ry="3" fill="#fff" opacity="0.95" />
      <path d="M15 16v16c0 1.7 4 3 9 3s9-1.3 9-3V16" fill="none" stroke="#fff" strokeWidth="1.8" />
      <path d="M15 24c0 1.7 4 3 9 3s9-1.3 9-3" fill="none" stroke="#fff" strokeWidth="1.5" opacity="0.8" />
    </svg>
  );
}

export function GearIcon({ size = 28 }) {
  // GitHub Actions — generic workflow tile (neutral)
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <rect width="48" height="48" rx="7" fill="#1f2430" />
      <circle cx="24" cy="24" r="8" fill="none" stroke="#8b93a7" strokeWidth="2" />
      <circle cx="24" cy="24" r="2.6" fill="#8b93a7" />
      <g stroke="#8b93a7" strokeWidth="2" strokeLinecap="round">
        <path d="M24 12v3M24 33v3M12 24h3M33 24h3M15.5 15.5l2.1 2.1M30.4 30.4l2.1 2.1M32.5 15.5l-2.1 2.1M17.6 30.4l-2.1 2.1" />
      </g>
    </svg>
  );
}

export function ScreenIcon({ size = 28 }) {
  // Dashboard / Vercel-style serving tile
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <rect width="48" height="48" rx="7" fill="#0b0d12" stroke="#2a3344" strokeWidth="1" />
      <path d="M24 13l10 18H14z" fill="#fff" />
    </svg>
  );
}
