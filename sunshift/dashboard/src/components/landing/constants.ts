import type { LucideIcon } from 'lucide-react';
import {
  BarChart3, CloudLightning, DollarSign, Lock, Server, Zap,
} from 'lucide-react';

export const REPO_URL = 'https://github.com/Kaydenletk/SunShift';
export const REPO_BLOB_URL = `${REPO_URL}/blob/main`;
export const REPO_TREE_URL = `${REPO_URL}/tree/main`;

export type MenuItem = { label: string; href: string };

export const menuItems: readonly MenuItem[] = [
  { label: 'Features', href: '/#features' },
  { label: 'Architecture', href: '/#architecture' },
  { label: 'Pricing', href: '/#pricing' },
  { label: 'Docs', href: '/#docs' },
] as const;

export const techBadges = [
  'AWS',
  'Terraform',
  'Docker',
  'FastAPI',
  'Next.js',
  'PostgreSQL',
  'HIPAA Certified',
  'SOC 2 Ready',
] as const;

export type RiskStat = { stat: string; label: string; source: string };

export const riskStats: readonly RiskStat[] = [
  { stat: '60%', label: 'of Florida SMBs never reopen after a natural disaster', source: 'FEMA' },
  { stat: '58%', label: 'of backups fail when recovery is actually attempted', source: '' },
  { stat: '11 days', label: 'without power for some Tampa businesses after Hurricane Milton', source: '2024' },
] as const;

export type Feature = {
  icon: LucideIcon;
  title: string;
  description: string;
  href: string;
  ctaLabel: string;
  external?: boolean;
};

export const features: readonly Feature[] = [
  {
    icon: CloudLightning,
    title: 'When a hurricane hits, your data is already 920 miles away',
    description:
      'SunShift watches NOAA storm alerts 24/7. When a hurricane threatens Tampa Bay, it automatically backs up everything to AWS Ohio — completely outside any Florida hurricane path. You get notified. Nothing breaks.',
    href: `${REPO_BLOB_URL}/sunshift/backend/services/hurricane_shield.py`,
    ctaLabel: 'View hurricane_shield.py',
    external: true,
  },
  {
    icon: Lock,
    title: 'Bank-level encryption from your office to Ohio and back',
    description:
      'Every file is AES-256 encrypted before it leaves your server. Every access is logged automatically. HIPAA-ready infrastructure — no scrambling when regulators ask for proof.',
    href: `${REPO_BLOB_URL}/docs/adr/004-hipaa-compliance.md`,
    ctaLabel: 'Read ADR-004: HIPAA Compliance',
    external: true,
  },
  {
    icon: Server,
    title: 'Power goes out in Tampa. Your team keeps working.',
    description:
      'A lightweight Python asyncio daemon monitors your server health every minute. If your office loses power or connectivity, SunShift fails over to the cloud automatically. Average failover: 4 minutes. Failback is automatic too.',
    href: `${REPO_TREE_URL}/sunshift/agent`,
    ctaLabel: 'View agent runtime',
    external: true,
  },
  {
    icon: BarChart3,
    title: 'Check everything from your phone. In plain English.',
    description:
      "Next.js dashboard with 60-second auto-refresh. See if your server is running, when the last backup happened, and how much you've saved this month. Three states: Protected, Peak, Hurricane. Green means good.",
    href: '/dashboard',
    ctaLabel: 'Open live dashboard',
  },
  {
    icon: Zap,
    title: 'SunShift finds the cheapest hours to run your server. Automatically.',
    description:
      'Tampa FPL rates swing from 6¢ to 27¢/kWh during peak hours. A Prophet + XGBoost ensemble forecasts costs 48h ahead with 87% accuracy. Heavy workloads shift to off-peak windows — customers save $100–150/month.',
    href: `${REPO_BLOB_URL}/sunshift/backend/ml/model.py`,
    ctaLabel: 'View model.py (Prophet + XGBoost)',
    external: true,
  },
  {
    icon: DollarSign,
    title: "Tax season hits. Your server doesn't choke.",
    description:
      'Hybrid Greedy + Lookahead scheduler picks the cheapest migration window dynamically. Burst to the cloud during demand peaks, pull back when the rush ends. No new hardware for a two-month problem.',
    href: `${REPO_BLOB_URL}/sunshift/backend/services/scheduler_service.py`,
    ctaLabel: 'View scheduler_service.py',
    external: true,
  },
] as const;

export type StoryMoment = {
  icon: LucideIcon;
  moment: string;
  description: string;
  tech: string;
  href: string;
  ctaLabel: string;
  external?: boolean;
};

export const storyMoments: readonly StoryMoment[] = [
  {
    icon: Server,
    moment: 'Right now, while you work',
    description:
      'Your files live on your office server — fast, local, under your control. In the background, SunShift quietly syncs everything to a secure vault in Ohio. Your team never notices.',
    tech: 'Python asyncio daemon · AES-256 S3 Transfer Acceleration · WebSocket',
    href: `${REPO_TREE_URL}/sunshift/agent`,
    ctaLabel: 'View agent code',
    external: true,
  },
  {
    icon: CloudLightning,
    moment: 'When a storm is coming',
    description:
      'SunShift polls NOAA every 30 minutes. When a hurricane threatens Tampa Bay, it automatically migrates your operations to Ohio — hours before landfall. Your team can keep working from laptops, phones, anywhere.',
    tech: 'FastAPI + EventBridge · 5-level threat scale · < 15-min RTO',
    href: `${REPO_TREE_URL}/sunshift/backend`,
    ctaLabel: 'Explore backend services',
    external: true,
  },
  {
    icon: DollarSign,
    moment: 'When electricity prices spike',
    description:
      'Florida power rates change every hour. When FPL rates spike 4.5×, SunShift shifts heavy computing to the cloud where it costs less. When rates drop, it shifts back. You see the savings on your next bill.',
    tech: 'Prophet + XGBoost ensemble · 48h lookahead · Hybrid Greedy scheduler',
    href: '/dashboard',
    ctaLabel: 'Open live dashboard',
  },
] as const;

export const trustItems = [
  { label: 'Bank-level encryption', sub: 'AES-256 before files leave your office' },
  { label: 'Weather checked every 30 min', sub: 'NOAA NHC integration, 24/7' },
  { label: '99.99% uptime', sub: 'Less than 1 hour of downtime per year' },
  { label: 'Fully automatic', sub: 'No phone calls, no IT guy required' },
] as const;

export const adrLinks = [
  { id: 'ADR-001', title: 'Hybrid Cloud Architecture', href: `${REPO_BLOB_URL}/docs/adr/001-hybrid-cloud-architecture.md` },
  { id: 'ADR-002', title: 'AWS Ohio Destination',      href: `${REPO_BLOB_URL}/docs/adr/002-aws-ohio-destination.md` },
  { id: 'ADR-003', title: 'TOU-Based Scheduling',      href: `${REPO_BLOB_URL}/docs/adr/003-tou-based-scheduling.md` },
  { id: 'ADR-004', title: 'HIPAA Compliance',          href: `${REPO_BLOB_URL}/docs/adr/004-hipaa-compliance.md` },
  { id: 'ADR-005', title: 'Hurricane Shield',          href: `${REPO_BLOB_URL}/docs/adr/005-hurricane-shield.md` },
] as const;
