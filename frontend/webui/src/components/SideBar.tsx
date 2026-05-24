import React, { useEffect, useRef, useState } from 'react';
import './SideBar.css';
import type { Message } from '../types/message';
import { useTranslation } from 'react-i18next';
import {
  SquarePen,
  History,
  CheckCircle2,
  RefreshCw,
  Search,
  X,
  ChevronRight,
  ChevronDown,
  Plus,
  Bot,
  Network,
  Factory,
  Settings2,
  Users,
} from 'lucide-react';

interface SideBarProps {
  isOpen: boolean;
  onClose: () => void;
  messages?: Message[];
  onNavigate?: (id: number) => void;
  currentConfig?: string;
  agentType?: 'simple' | 'orchestra' | 'orchestrator' | 'other';
  subAgents?: string[] | null;
  onConfigSelect?: (config: string) => void;
  handleAddConfig?: () => void;
  getConfigList: () => void;
  availableConfigs: string[];
  showNewChatButton?: boolean;
  showAgentConfigs?: boolean;
}

// ── Config categorisation ──────────────────────────────────────────────────

const MFG_KEYWORDS = ['sensor_sage', 'industrial_qa', 'case_detective'];
const MULTI_KEYWORDS = ['orchestra', 'orchestrator'];

type ConfigCategory = 'manufacturing' | 'multi' | 'single';

function getCategory(config: string): ConfigCategory {
  const key = config.toLowerCase();
  if (MFG_KEYWORDS.some(k => key.includes(k))) return 'manufacturing';
  if (MULTI_KEYWORDS.some(k => key.includes(k))) return 'multi';
  return 'single';
}

const CATEGORY_META: Record<ConfigCategory, { label: string; Icon: React.ElementType; badge: string; badgeClass: string }> = {
  manufacturing: {
    label: 'Smart Manufacturing',
    Icon: Factory,
    badge: 'MFG',
    badgeClass: 'sb-badge sb-badge-mfg',
  },
  multi: {
    label: 'Multi-Agent',
    Icon: Network,
    badge: 'MULTI',
    badgeClass: 'sb-badge sb-badge-multi',
  },
  single: {
    label: 'Single Agent',
    Icon: Bot,
    badge: 'AGENT',
    badgeClass: 'sb-badge sb-badge-single',
  },
};

const CATEGORY_ORDER: ConfigCategory[] = ['manufacturing', 'multi', 'single'];

// ── Filename display ───────────────────────────────────────────────────────

function getFilename(path: string): string {
  const filename = path.split('/').pop() || '';
  return filename
    .replace(/\.ya?ml$/, '')
    .split(/[_-]/)
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

// ── Tooltip ────────────────────────────────────────────────────────────────

const Tooltip = ({ content, children }: { content: string; children: React.ReactNode }) => {
  const [hovered, setHovered] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0 });
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && hovered) {
      const r = ref.current.getBoundingClientRect();
      setPos({ left: r.right + window.scrollX + 10, top: r.top + window.scrollY + r.height / 2 });
    }
  }, [hovered]);

  return (
    <div ref={ref} className="tooltip-container" onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}>
      {children}
      {hovered && (
        <div className="tooltip" style={{ left: pos.left, top: pos.top }}>
          {content}
        </div>
      )}
    </div>
  );
};

// ── Main Component ─────────────────────────────────────────────────────────

const SideBar: React.FC<SideBarProps> = ({
  isOpen,
  onClose,
  messages = [],
  onNavigate = () => {},
  currentConfig = '',
  agentType = 'simple',
  subAgents = null,
  onConfigSelect = () => {},
  handleAddConfig = () => {},
  getConfigList,
  availableConfigs = [],
  showNewChatButton = true,
  showAgentConfigs = true,
}) => {
  const sidebarRef = useRef<HTMLDivElement>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const COLLAPSE_KEY = 'sidebar.availableConfigsCollapsed';
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try { return window.localStorage.getItem(COLLAPSE_KEY) === 'true'; } catch { return false; }
  });
  const { t } = useTranslation();

  // Load configs once on mount
  useEffect(() => {
    if (availableConfigs.length === 0) getConfigList();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Persist collapse state
  useEffect(() => {
    try { window.localStorage.setItem(COLLAPSE_KEY, String(isCollapsed)); } catch { /* noop */ }
  }, [isCollapsed]);

  // Close sidebar on outside click (mobile)
  useEffect(() => {
    if (window.innerWidth > 768) return;
    const handle = (e: MouseEvent) => {
      if (sidebarRef.current && !sidebarRef.current.contains(e.target as Node)) onClose();
    };
    if (isOpen) document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, [isOpen, onClose]);

  const handleNewChat = () => window.open(window.location.href, '_blank');

  // Group configs by category
  const filteredConfigs = availableConfigs
    .filter(c => c.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => getFilename(a).localeCompare(getFilename(b)));

  const grouped = CATEGORY_ORDER.reduce<Record<ConfigCategory, string[]>>(
    (acc, cat) => { acc[cat] = filteredConfigs.filter(c => getCategory(c) === cat); return acc; },
    { manufacturing: [], multi: [], single: [] }
  );

  const agentHistory = messages.filter(m => m.type === 'new_agent' && typeof m.content === 'string');

  return (
    <div ref={sidebarRef} className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <div className="sidebar-content">

        {/* ── New Chat ── */}
        {showNewChatButton && (
          <>
            <button className="sb-new-chat" onClick={handleNewChat}>
              <SquarePen size={14} strokeWidth={2} />
              {t('sidebar.newChat')}
            </button>
            <div className="sb-divider" />
          </>
        )}

        {/* ── Agent History ── */}
        <div className="sidebar-section">
          <div className="sb-category-label">
            <History size={11} strokeWidth={2} />
            {t('sidebar.agentHistoryTitle')}
          </div>
          {agentHistory.length > 0 ? (
            agentHistory.map(msg => (
              <div
                key={msg.id}
                className="sb-item"
                onClick={() => onNavigate(Number(msg.id))}
              >
                <span style={{ fontSize: 13 }}>🐙</span>
                <span className="sb-item-label">{msg.content as string}</span>
              </div>
            ))
          ) : (
            <div className="sb-empty">{t('sidebar.noHistoryShort')}</div>
          )}
        </div>

        <div className="sb-divider" />

        {/* ── Current Config ── */}
        {currentConfig && (
          <div className="sidebar-section">
            <div className="sb-category-label">
              <CheckCircle2 size={11} strokeWidth={2.5} />
              {t('sidebar.currentConfigTitle')}
            </div>

            <div className="sb-current-card">
              <div className="sb-current-header">
                {getCategory(currentConfig) === 'manufacturing'
                  ? <Factory size={14} strokeWidth={1.5} />
                  : getCategory(currentConfig) === 'multi'
                  ? <Network size={14} strokeWidth={1.5} />
                  : <Bot size={14} strokeWidth={1.5} />}
                <span>{getFilename(currentConfig)}</span>
              </div>
              <div className="sb-current-path">{currentConfig}</div>

              {(agentType === 'orchestra' || agentType === 'orchestrator') && subAgents && subAgents.length > 0 && (
                <div className="sb-subagents">
                  <div className="sb-subagents-label"><Users size={10} style={{ display: 'inline', marginRight: 4 }} />{t('sidebar.subAgentsTitle')}</div>
                  {subAgents.map((a, i) => <div key={i} className="sb-subagent-row">· {a}</div>)}
                </div>
              )}
            </div>

            <div className="sb-add-link" onClick={handleAddConfig}>
              <Plus size={13} strokeWidth={2} />
              {t('sidebar.addNewConfig')}
            </div>
          </div>
        )}

        {/* ── Available Configs ── */}
        {showAgentConfigs && (
          <>
            <div className="sb-divider" />
            <div className="sidebar-section">
              <div className="sb-section-header">
                <span className="sb-section-title">{t('sidebar.availableConfigsTitle')}</span>
                <button
                  className={`sb-refresh ${isRefreshing ? 'spinning' : ''}`}
                  onClick={() => { setIsRefreshing(true); getConfigList(); setTimeout(() => setIsRefreshing(false), 1000); }}
                  disabled={isRefreshing}
                  title={t('sidebar.refreshConfigs')}
                >
                  <RefreshCw size={13} strokeWidth={2} />
                </button>
              </div>

              {/* Search */}
              <div className="sb-search">
                <Search size={12} strokeWidth={2} className="sb-search-icon" />
                <input
                  type="text"
                  placeholder={t('sidebar.searchConfigs')}
                  value={searchTerm}
                  onFocus={() => { if (isCollapsed) setIsCollapsed(false); }}
                  onChange={e => { setSearchTerm(e.target.value); if (e.target.value && isCollapsed) setIsCollapsed(false); }}
                />
                {searchTerm && (
                  <button className="sb-search-clear" onClick={() => setSearchTerm('')} title={t('sidebar.clearSearch')}>
                    <X size={12} strokeWidth={2} />
                  </button>
                )}
              </div>

              {/* Collapse toggle */}
              <div className="sb-collapse-row">
                <button className="sb-collapse-btn" onClick={() => setIsCollapsed(p => !p)} aria-expanded={!isCollapsed}>
                  {isCollapsed
                    ? <ChevronRight size={12} strokeWidth={2} />
                    : <ChevronDown size={12} strokeWidth={2} />}
                  {isCollapsed ? t('sidebar.expand') : t('sidebar.collapse')}
                </button>
              </div>

              {/* Grouped config list */}
              {!isCollapsed && (
                <div className="sb-config-list">
                  {CATEGORY_ORDER.map(cat => {
                    const items = grouped[cat];
                    if (items.length === 0) return null;
                    const { label, Icon, badgeClass, badge } = CATEGORY_META[cat];
                    return (
                      <div key={cat} className="sb-category-group">
                        <div className="sb-category-label" style={{ paddingTop: 10, paddingBottom: 4 }}>
                          <Icon size={11} strokeWidth={2} />
                          {label}
                        </div>
                        {items.map(config => (
                          <Tooltip key={config} content={config}>
                            <div
                              className={`sb-item ${currentConfig === config ? 'active' : ''}`}
                              onClick={() => onConfigSelect(config)}
                            >
                              <Settings2 size={12} strokeWidth={1.5} style={{ flexShrink: 0, opacity: 0.5 }} />
                              <span className="sb-item-label">{getFilename(config)}</span>
                              <span className={badgeClass}>{badge}</span>
                            </div>
                          </Tooltip>
                        ))}
                      </div>
                    );
                  })}
                  {filteredConfigs.length === 0 && (
                    <div className="sb-empty">
                      {availableConfigs.length === 0 ? t('sidebar.noConfigsShort') : t('sidebar.noMatchingConfigs')}
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default SideBar;
