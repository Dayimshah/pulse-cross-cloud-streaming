// Lightweight inline SVG service marks. Simplified, recognizable silhouettes
// (not official assets) so the architecture diagram reads as real infrastructure.

export function KafkaIcon({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="4" r="2.2" fill="#a970ff" />
      <circle cx="7" cy="12" r="2.2" fill="#a970ff" />
      <circle cx="17" cy="12" r="2.2" fill="#a970ff" />
      <circle cx="12" cy="20" r="2.2" fill="#a970ff" />
      <path d="M12 6.2v2.4M12 15.4v2.4M9 11l1.6-3.2M15 11l-1.6-3.2M9 13l1.6 3.2M15 13l-1.6 3.2"
        stroke="#a970ff" strokeWidth="1.3" />
    </svg>
  );
}

export function S3Icon({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M5 6c0-1 3.1-2 7-2s7 1 7 2v12c0 1-3.1 2-7 2s-7-1-7-2V6z" fill="#ff9900" opacity="0.18" />
      <ellipse cx="12" cy="6" rx="7" ry="2" stroke="#ff9900" strokeWidth="1.4" />
      <path d="M5 6v12c0 1.1 3.1 2 7 2s7-.9 7-2V6" stroke="#ff9900" strokeWidth="1.4" />
      <path d="M5 12c0 1.1 3.1 2 7 2s7-.9 7-2" stroke="#ff9900" strokeWidth="1.1" opacity="0.7" />
    </svg>
  );
}

export function DynamoIcon({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <rect x="4" y="5" width="16" height="14" rx="2" fill="#ff9900" opacity="0.12" stroke="#ff9900" strokeWidth="1.3" />
      <path d="M8 9h8M8 12h8M8 15h5" stroke="#ff9900" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}

export function CosmosIcon({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="7.5" stroke="#3aa0ff" strokeWidth="1.4" fill="#3aa0ff" fillOpacity="0.12" />
      <ellipse cx="12" cy="12" rx="7.5" ry="3" stroke="#3aa0ff" strokeWidth="1.1" transform="rotate(30 12 12)" />
      <ellipse cx="12" cy="12" rx="7.5" ry="3" stroke="#3aa0ff" strokeWidth="1.1" transform="rotate(-30 12 12)" />
      <circle cx="12" cy="12" r="1.6" fill="#3aa0ff" />
    </svg>
  );
}

export function LakeIcon({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M4 7h16M4 12h16M4 17h16" stroke="#3aa0ff" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="7" cy="7" r="1.1" fill="#3aa0ff" />
      <circle cx="7" cy="12" r="1.1" fill="#3aa0ff" />
      <circle cx="7" cy="17" r="1.1" fill="#3aa0ff" />
    </svg>
  );
}

export function GearIcon({ size = 26, color = "#8b93a7" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M12 8a4 4 0 100 8 4 4 0 000-8z" stroke={color} strokeWidth="1.4" />
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"
        stroke={color} strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}

export function ScreenIcon({ size = 26, color = "#35e0c8" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <rect x="3" y="4" width="18" height="12" rx="2" stroke={color} strokeWidth="1.4" />
      <path d="M8 20h8M12 16v4" stroke={color} strokeWidth="1.4" strokeLinecap="round" />
      <path d="M6.5 11l2.5-2.5 2 2 3.5-3.5" stroke={color} strokeWidth="1.3" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
