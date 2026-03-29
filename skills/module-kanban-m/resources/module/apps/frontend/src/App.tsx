import { useEffect, useMemo, useState } from 'react';
import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';

type Priority = 'low' | 'normal' | 'high' | 'urgent';

type Member = {
  id: number;
  name: string;
  role: string;
};

type Task = {
  id: number;
  code: string;
  title: string;
  description: string;
  priority: Priority;
  archived: boolean;
  column_id: number;
  assignee_id: number | null;
  updated_at: string;
};

type BoardColumn = {
  id: number;
  name: string;
  order: number;
  tasks: Task[];
};

type BoardResponse = {
  workspace_name: string;
  columns: BoardColumn[];
  members: Member[];
};

type TeamMetrics = {
  workload: Record<string, number>;
  member_metrics: { member: Member; total_tasks: number; doing_tasks: number; done_tasks: number }[];
  recent_activity: { id: number; action: string; details: string; created_at: string }[];
};

type WorkspaceSettings = {
  workspace_name: string;
  theme: 'light' | 'dark';
};

const POOL_META: Record<string, { label: string; zh: string; order: number; badgeClass?: string }> = {
  Backlog: { label: 'Backlog', zh: '预备池', order: 1 },
  Ready: { label: 'Ready', zh: '就绪池', order: 2 },
  Doing: { label: 'Doing', zh: '执行池', order: 3 },
  Done: { label: 'Done', zh: '完成池', order: 4 },
  Blocked: { label: 'Blocked', zh: '阻塞池', order: 5, badgeClass: 'bg-error-container text-on-error-container' },
  Waiting: { label: 'Waiting', zh: '等待池', order: 6 },
};

const LANE_VISUAL_CLASS: Record<string, string> = {
  Backlog: 'bg-slate-200 border border-slate-400',
  Ready: 'bg-slate-300/80 border border-slate-500/80',
  Doing: 'bg-slate-400/70 border border-slate-600/80',
  Done: 'bg-slate-300/75 border border-slate-500/80',
  Blocked: 'bg-slate-500/55 border border-slate-700/80',
  Waiting: 'bg-slate-600/40 border border-slate-700/80',
};

const PRIORITY_ZH: Record<Priority, string> = {
  low: '低',
  normal: '普通',
  high: '高',
  urgent: '紧急',
};

function toZhColumn(name: string): string {
  return POOL_META[name]?.zh ?? name;
}

function toBilingualColumn(name: string): string {
  const meta = POOL_META[name];
  if (!meta) return name;
  return `${meta.label} (${meta.zh})`;
}

function extractEstimate(description: string): { cleanDescription: string; estimate: string | null } {
  const match = description.match(/\[\[ETA:(.+?)\]\]/);
  if (!match) return { cleanDescription: description, estimate: null };
  return {
    cleanDescription: description.replace(match[0], '').trim(),
    estimate: match[1].trim(),
  };
}

const ETA_MINUTES_OPTIONS = Array.from({ length: 20 }, (_, i) => 25 + i * 5).filter((m) => m <= 120);

function etaLabel(minutes: number): string {
  if (minutes < 60) return `${minutes}分钟`;
  if (minutes === 60) return '1小时';
  const h = Math.floor(minutes / 60);
  const r = minutes % 60;
  return r === 0 ? `${h}小时` : `${h}小时${r}分钟`;
}

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://127.0.0.1:8001';

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return (await res.json()) as T;
}

function TopNavBar() {
  return (
    <header className="fixed top-0 w-full z-50 bg-slate-50/80 backdrop-blur-xl flex items-center justify-between px-6 h-16 border-b border-slate-100">
      <div className="flex items-center gap-8">
        <Link to="/" className="text-xl font-bold tracking-tight text-slate-900 font-headline">
          建筑画布
        </Link>
        <nav className="hidden md:flex items-center gap-6 font-manrope text-sm font-medium">
          <Link to="/" className="text-blue-600 font-semibold">工作台</Link>
          <Link to="/team" className="text-slate-500 hover:bg-slate-200/50 transition-colors px-2 py-1 rounded">团队分析</Link>
          <span className="text-slate-500 px-2 py-1">文档</span>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative hidden sm:block">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">search</span>
          <input className="bg-surface-container-high border-none rounded-sm pl-10 pr-4 py-1.5 text-sm w-64" placeholder="Search tasks..." type="text" readOnly />
        </div>
        <button className="p-2 text-on-surface-variant hover:bg-slate-200/50 rounded-full">
          <span className="material-symbols-outlined">notifications</span>
        </button>
      </div>
    </header>
  );
}

function SideNavBar() {
  const location = useLocation();
  const path = location.pathname;
  const navClass = (itemPath: string) =>
    `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${path === itemPath ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'}`;

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] w-64 bg-slate-50 border-r border-slate-100 flex flex-col p-4 gap-2 font-inter text-sm font-medium hidden lg:flex">
      <div className="flex items-center gap-3 px-2 py-4 mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-on-primary">
          <span className="material-symbols-outlined">architecture</span>
        </div>
        <div>
          <p className="font-bold text-on-surface leading-tight">项目 Alpha</p>
          <p className="text-xs text-on-surface-variant">主工作区</p>
        </div>
      </div>
      <Link to="/" className={navClass('/')}> <span className="material-symbols-outlined">dashboard</span> <span>我的看板</span> </Link>
      <Link to="/team" className={navClass('/team')}> <span className="material-symbols-outlined">group</span> <span>团队视图</span> </Link>
      <Link to="/archive" className={navClass('/archive')}> <span className="material-symbols-outlined">archive</span> <span>归档</span> </Link>
      <Link to="/settings" className={navClass('/settings')}> <span className="material-symbols-outlined">settings</span> <span>设置</span> </Link>
      <div className="mt-auto">
        <button className="w-full flex items-center justify-center gap-2 bg-primary text-on-primary py-2.5 rounded-xl font-bold">
          <span className="material-symbols-outlined text-sm">add</span>
          新建项目
        </button>
      </div>
    </aside>
  );
}

function DashboardPage() {
  const [board, setBoard] = useState<BoardResponse | null>(null);
  const [keyword, setKeyword] = useState('');
  const [draggingTaskId, setDraggingTaskId] = useState<number | null>(null);
  const [dragOverColumnId, setDragOverColumnId] = useState<number | null>(null);
  const [dragOverTaskId, setDragOverTaskId] = useState<number | null>(null);
  const [dropPreview, setDropPreview] = useState<{ columnId: number; index: number } | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState<{
    title: string;
    description: string;
    priority: Priority;
    column_id: number;
    assignee_id: number | null;
    estimateMinutes: number;
  }>({
    title: '',
    description: '',
    priority: 'normal',
    column_id: 0,
    assignee_id: null,
    estimateMinutes: 25,
  });

  async function load() {
    setBoard(await api<BoardResponse>('/board'));
  }

  useEffect(() => {
    void load();
  }, []);

  const filtered = useMemo(() => {
    if (!board) return null;
    const byName = new Map(board.columns.map((c) => [c.name, c]));
    const ordered = Object.keys(POOL_META)
      .map((name) => {
        const found = byName.get(name);
        if (found) return found;
        return {
          id: -POOL_META[name].order,
          name,
          order: POOL_META[name].order,
          tasks: [],
        } as BoardColumn;
      })
      .sort((a, b) => (POOL_META[a.name]?.order ?? 999) - (POOL_META[b.name]?.order ?? 999));

    return {
      ...board,
      columns: ordered.map((c) => ({
        ...c,
        tasks: c.tasks.filter((t) => `${t.title} ${t.description}`.toLowerCase().includes(keyword.toLowerCase())),
      })),
    };
  }, [board, keyword]);

  function openCreateModal() {
    if (!board || board.columns.length === 0) return;
    const backlogColumn = board.columns.find((c) => c.name === 'Backlog') ?? board.columns[0];
    setCreateForm({
      title: '',
      description: '',
      priority: 'normal',
      column_id: backlogColumn.id,
      assignee_id: board.members[0]?.id ?? null,
      estimateMinutes: 25,
    });
    setShowCreateModal(true);
  }

  async function createTaskByForm() {
    if (!board || !createForm.title.trim()) return;
    setCreating(true);
    try {
      await api('/tasks', {
        method: 'POST',
        body: JSON.stringify({
          title: createForm.title.trim(),
          description: `${createForm.description.trim()} [[ETA:${etaLabel(createForm.estimateMinutes)}]]`.trim(),
          priority: createForm.priority,
          column_id: createForm.column_id,
          assignee_id: createForm.assignee_id,
        }),
      });
      setShowCreateModal(false);
      await load();
    } finally {
      setCreating(false);
    }
  }

  async function moveTaskWithDnD(taskId: number, toColumnId: number) {
    if (!board) return;

    const fromColumn = board.columns.find((c) => c.tasks.some((t) => t.id === taskId));
    if (!fromColumn || fromColumn.id === toColumnId) return;

    const prevBoard = board;
    const nextColumns = board.columns.map((col) => {
      if (col.id === fromColumn.id) {
        return { ...col, tasks: col.tasks.filter((t) => t.id !== taskId) };
      }
      if (col.id === toColumnId) {
        const movedTask = fromColumn.tasks.find((t) => t.id === taskId);
        if (!movedTask) return col;
        return { ...col, tasks: [...col.tasks, { ...movedTask, column_id: toColumnId }] };
      }
      return col;
    });
    setBoard({ ...board, columns: nextColumns });

    try {
      await api(`/tasks/${taskId}/move`, {
        method: 'PATCH',
        body: JSON.stringify({ column_id: toColumnId }),
      });
      await load();
    } catch {
      setBoard(prevBoard);
    }
  }

  async function moveTaskToPosition(taskId: number, toColumnId: number, toIndex: number) {
    if (!board) return;

    const fromColumn = board.columns.find((c) => c.tasks.some((t) => t.id === taskId));
    if (!fromColumn) return;
    const movingTask = fromColumn.tasks.find((t) => t.id === taskId);
    if (!movingTask) return;
    const fromIndex = fromColumn.tasks.findIndex((t) => t.id === taskId);

    const prevBoard = board;
    const normalizedIndex = Math.max(0, toIndex);

    const nextColumns = board.columns.map((col) => {
      if (col.id === fromColumn.id && col.id === toColumnId) {
        const tasksWithout = col.tasks.filter((t) => t.id !== taskId);
        const adjustedIndex = normalizedIndex > fromIndex ? normalizedIndex - 1 : normalizedIndex;
        const insertAt = Math.min(Math.max(0, adjustedIndex), tasksWithout.length);
        return {
          ...col,
          tasks: [
            ...tasksWithout.slice(0, insertAt),
            { ...movingTask, column_id: toColumnId },
            ...tasksWithout.slice(insertAt),
          ],
        };
      }

      if (col.id === fromColumn.id) {
        return { ...col, tasks: col.tasks.filter((t) => t.id !== taskId) };
      }

      if (col.id === toColumnId) {
        const insertAt = Math.min(normalizedIndex, col.tasks.length);
        return {
          ...col,
          tasks: [
            ...col.tasks.slice(0, insertAt),
            { ...movingTask, column_id: toColumnId },
            ...col.tasks.slice(insertAt),
          ],
        };
      }

      return col;
    });

    setBoard({ ...board, columns: nextColumns });

    try {
      if (fromColumn.id !== toColumnId) {
        await api(`/tasks/${taskId}/move`, {
          method: 'PATCH',
          body: JSON.stringify({ column_id: toColumnId }),
        });
        await load();
      }
    } catch {
      setBoard(prevBoard);
    }
  }

  return (
    <div className="flex-1 lg:ml-64 pt-16 h-screen flex flex-col overflow-hidden">
      <div className="px-8 py-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold font-headline text-on-surface tracking-tight">开发迭代 24</h1>
          <p className="text-on-surface-variant text-sm mt-1">Q3 架构升级的执行任务流水线。</p>
        </div>
        <div className="flex items-center gap-3">
          <input value={keyword} onChange={(e) => setKeyword(e.target.value)} className="px-3 py-2 rounded-lg bg-surface-container-low" placeholder="筛选任务" />
          <button onClick={openCreateModal} className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-semibold shadow-sm">
            <span className="material-symbols-outlined text-lg">add</span>
            新建任务
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-x-auto overflow-y-hidden px-8 pb-8 flex gap-6">
        {filtered?.columns.map((col) => (
          <div
            key={col.id}
            className={`flex-none w-80 flex flex-col h-full rounded-xl p-3 shadow-sm ${LANE_VISUAL_CLASS[col.name] ?? 'bg-slate-100 border border-slate-200'}`}
            onDragOver={(e) => {
              e.preventDefault();
              // Only fallback to tail-drop when hovering the lane container itself.
              if (e.target !== e.currentTarget) return;
              setDragOverColumnId(col.id);
              setDropPreview({ columnId: col.id, index: col.tasks.length });
            }}
            onDragLeave={() => {
              setDragOverColumnId((current) => (current === col.id ? null : current));
              setDragOverTaskId(null);
              setDropPreview((current) => (current?.columnId === col.id ? null : current));
            }}
            onDrop={async (e) => {
              e.preventDefault();
              e.stopPropagation();
              const taskId = Number(e.dataTransfer.getData('text/task-id') || 0);
              const targetIndex = dropPreview?.columnId === col.id ? dropPreview.index : col.tasks.length;
              setDragOverColumnId(null);
              setDragOverTaskId(null);
              setDropPreview(null);
              if (!taskId) return;
              await moveTaskToPosition(taskId, col.id, targetIndex);
            }}
          >
            <div className="flex items-center justify-between mb-4 px-1">
              <div className="flex items-center gap-2">
                <h2 className="font-headline font-bold text-on-surface">{toBilingualColumn(col.name)}</h2>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                    POOL_META[col.name]?.badgeClass ?? 'bg-surface-container-highest text-on-surface-variant'
                  }`}
                >
                  {col.tasks.length}
                </span>
              </div>
            </div>
            <div className={`flex-1 overflow-y-auto space-y-4 pr-1 rounded-lg transition-colors ${dragOverColumnId === col.id ? 'bg-white/35' : ''}`}>
              {col.tasks.map((task, index) => (
                <div key={task.id}>
                  {dropPreview?.columnId === col.id && dropPreview.index === index ? (
                    <div className="h-2 -mt-1 mb-2 rounded-full bg-primary/35 border border-primary/40" />
                  ) : null}
                  <div
                    className={`bg-white p-4 rounded-xl border border-slate-300 shadow-sm hover:shadow-md hover:border-primary/20 transition-all ${draggingTaskId === task.id ? 'opacity-50 scale-[0.98]' : ''} ${dragOverTaskId === task.id ? 'ring-2 ring-primary/30' : ''}`}
                    draggable
                    onDragStart={(e) => {
                      setDraggingTaskId(task.id);
                      e.dataTransfer.effectAllowed = 'move';
                      e.dataTransfer.setData('text/task-id', String(task.id));
                    }}
                    onDragEnd={() => {
                      setDraggingTaskId(null);
                      setDragOverColumnId(null);
                      setDragOverTaskId(null);
                      setDropPreview(null);
                    }}
                    onDragOver={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      const rect = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
                      const before = e.clientY < rect.top + rect.height / 2;
                      setDragOverColumnId(col.id);
                      setDragOverTaskId(task.id);
                      setDropPreview({ columnId: col.id, index: before ? index : index + 1 });
                    }}
                    onDrop={async (e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      const droppedTaskId = Number(e.dataTransfer.getData('text/task-id') || 0);
                      const targetIndex = dropPreview?.columnId === col.id ? dropPreview.index : index;
                      setDragOverColumnId(null);
                      setDragOverTaskId(null);
                      setDropPreview(null);
                      if (!droppedTaskId) return;
                      await moveTaskToPosition(droppedTaskId, col.id, targetIndex);
                    }}
                  >
                  <div className="flex justify-between items-start mb-3">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wider bg-primary-container text-on-primary-container">{PRIORITY_ZH[task.priority]}</span>
                    <span className="text-[11px] font-mono text-on-surface-variant">#{task.code}</span>
                  </div>
                  <h3 className="text-sm font-bold text-on-surface mb-2 leading-snug">{task.title}</h3>
                  <p className="text-xs text-on-surface-variant mb-2 leading-relaxed">
                    {extractEstimate(task.description).cleanDescription || '暂无描述'}
                  </p>
                  {extractEstimate(task.description).estimate ? (
                    <div className="mb-3 flex items-center gap-1.5 text-[11px] text-on-surface-variant font-medium">
                      <span className="material-symbols-outlined text-sm">schedule</span>
                      <span>预估：{extractEstimate(task.description).estimate}</span>
                    </div>
                  ) : null}
                  <div className="flex items-center justify-between gap-2">
                    <select
                      className="text-xs rounded border px-2 py-1"
                      value={task.column_id}
                      onChange={async (e) => {
                        await api(`/tasks/${task.id}/move`, { method: 'PATCH', body: JSON.stringify({ column_id: Number(e.target.value) }) });
                        await load();
                      }}
                    >
                      {board?.columns.map((c) => (
                        <option key={c.id} value={c.id}>{toZhColumn(c.name)}</option>
                      ))}
                    </select>
                    <div className="flex gap-2">
                      <button className="text-xs px-2 py-1 rounded bg-slate-200 text-slate-700" onClick={async () => { await api(`/tasks/${task.id}/archive`, { method: 'POST' }); await load(); }}>归档</button>
                      <button className="text-xs px-2 py-1 rounded bg-rose-500 text-white" onClick={async () => { await api(`/tasks/${task.id}`, { method: 'DELETE' }); await load(); }}>删除</button>
                    </div>
                  </div>
                  </div>
                </div>
              ))}
              {dropPreview?.columnId === col.id && dropPreview.index === col.tasks.length ? (
                <div className="h-2 -mt-1 rounded-full bg-primary/35 border border-primary/40" />
              ) : null}
            </div>
          </div>
        ))}
      </div>

      {showCreateModal ? (
        <div className="fixed inset-0 z-[70] bg-black/30 flex items-center justify-center p-4" onClick={() => setShowCreateModal(false)}>
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-300 p-6" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-xl font-bold mb-4 text-slate-950">新建任务</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-800">标题</label>
                <input
                  className="w-full mt-1 rounded-lg border border-slate-500 bg-slate-50 text-slate-950 placeholder:text-slate-600 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/35 focus:border-primary"
                  value={createForm.title}
                  onChange={(e) => setCreateForm((v) => ({ ...v, title: e.target.value }))}
                  placeholder="请输入任务标题"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-800">描述</label>
                <textarea
                  className="w-full mt-1 rounded-lg border border-slate-500 bg-slate-50 text-slate-950 placeholder:text-slate-600 px-3 py-2 min-h-24 focus:outline-none focus:ring-2 focus:ring-primary/35 focus:border-primary"
                  value={createForm.description}
                  onChange={(e) => setCreateForm((v) => ({ ...v, description: e.target.value }))}
                  placeholder="请输入任务描述"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-800">优先级</label>
                  <select
                    className="w-full mt-1 rounded-lg border border-slate-500 bg-slate-50 text-slate-950 px-2 py-2 focus:outline-none focus:ring-2 focus:ring-primary/35 focus:border-primary"
                    value={createForm.priority}
                    onChange={(e) => setCreateForm((v) => ({ ...v, priority: e.target.value as Priority }))}
                  >
                    <option value="low">低</option>
                    <option value="normal">普通</option>
                    <option value="high">高</option>
                    <option value="urgent">紧急</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-800">负责人</label>
                  <select
                    className="w-full mt-1 rounded-lg border border-slate-500 bg-slate-50 text-slate-950 px-2 py-2 focus:outline-none focus:ring-2 focus:ring-primary/35 focus:border-primary"
                    value={createForm.assignee_id ?? ''}
                    onChange={(e) =>
                      setCreateForm((v) => ({
                        ...v,
                        assignee_id: e.target.value ? Number(e.target.value) : null,
                      }))
                    }
                  >
                    <option value="">未分配</option>
                    {board.members.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-800">预估时间（25分钟-2小时）</label>
                  <div className="text-sm font-semibold text-primary mt-1 mb-1 text-center">{etaLabel(createForm.estimateMinutes)}</div>
                  <div className="mt-1">
                    <select
                      className="w-full mt-1 rounded-lg border border-slate-500 bg-slate-50 text-slate-950 px-2 py-2 focus:outline-none focus:ring-2 focus:ring-primary/35 focus:border-primary"
                      value={createForm.estimateMinutes}
                      onChange={(e) => setCreateForm((v) => ({ ...v, estimateMinutes: Number(e.target.value) }))}
                    >
                      {ETA_MINUTES_OPTIONS.map((m) => (
                        <option key={m} value={m}>
                          {etaLabel(m)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <button className="px-4 py-2 rounded-lg bg-slate-300 text-slate-800 border border-slate-400 hover:bg-slate-200" onClick={() => setShowCreateModal(false)}>
                取消
              </button>
              <button
                className="px-4 py-2 rounded-lg bg-blue-700 text-white border border-blue-900 shadow-sm hover:bg-blue-800 active:bg-blue-900 disabled:bg-slate-300 disabled:text-slate-600 disabled:border-slate-400 disabled:opacity-100"
                disabled={creating || !createForm.title.trim()}
                onClick={() => void createTaskByForm()}
              >
                {creating ? '创建中...' : '提交创建'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function ArchivePage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  async function load() {
    setTasks(await api<Task[]>('/tasks?archived=true'));
  }
  useEffect(() => { void load(); }, []);

  return (
    <div className="flex-1 lg:ml-64 pt-16 h-screen flex flex-col bg-surface overflow-hidden">
      <div className="flex-1 overflow-y-auto px-8 pb-12 pt-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <h2 className="text-4xl font-extrabold font-manrope text-on-background leading-tight">项目归档</h2>
            <p className="text-on-surface-variant mt-2 max-w-xl">查看并管理历史任务。</p>
          </div>
        </div>
        <div className="bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-slate-100">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-low">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant">任务标识</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant">优先级</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant">更新时间</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant text-right">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-surface-bright transition-colors group">
                  <td className="px-6 py-5">
                    <p className="font-bold text-on-surface">{task.title}</p>
                    <p className="text-xs text-on-surface-variant">{task.code}</p>
                  </td>
                  <td className="px-6 py-5">{PRIORITY_ZH[task.priority]}</td>
                  <td className="px-6 py-5">{new Date(task.updated_at).toLocaleString()}</td>
                  <td className="px-6 py-5 text-right">
                    <button className="p-2 hover:bg-surface-container-high rounded-lg text-primary" onClick={async () => { await api(`/tasks/${task.id}/restore`, { method: 'POST' }); await load(); }}>
                      <span className="material-symbols-outlined text-xl">settings_backup_restore</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SettingsPage() {
  const [settings, setSettings] = useState<WorkspaceSettings | null>(null);
  const [workspaceName, setWorkspaceName] = useState('');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    void (async () => {
      const s = await api<WorkspaceSettings>('/workspace/settings');
      setSettings(s);
      setWorkspaceName(s.workspace_name);
      setTheme(s.theme);
    })();
  }, []);

  return (
    <div className="flex-1 lg:ml-64 pt-16 h-screen flex flex-col overflow-y-auto">
      <main className="p-10 max-w-5xl mx-auto w-full">
        <header className="mb-12">
          <h1 className="text-4xl font-extrabold font-headline tracking-tight text-on-surface mb-2">工作区设置</h1>
          <p className="text-on-surface-variant text-lg">管理团队环境与偏好配置。</p>
        </header>
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-bold font-headline mb-2">工作区配置</h3>
          </div>
          <div className="md:col-span-2 space-y-6">
            <input className="w-full bg-surface-container-low border-none rounded-lg px-4 py-3" value={workspaceName} onChange={(e) => setWorkspaceName(e.target.value)} />
            <div className="grid grid-cols-2 gap-4">
              <label className="relative cursor-pointer group">
                <input checked={theme === 'light'} onChange={() => setTheme('light')} className="peer sr-only" name="theme" type="radio" />
                <div className="p-4 rounded-xl bg-surface-container-lowest border-2 border-transparent peer-checked:border-primary flex flex-col items-center gap-3">
                  <span className="material-symbols-outlined text-3xl text-on-surface-variant">light_mode</span>
                  <span className="font-semibold text-sm">浅色模式</span>
                </div>
              </label>
              <label className="relative cursor-pointer group">
                <input checked={theme === 'dark'} onChange={() => setTheme('dark')} className="peer sr-only" name="theme" type="radio" />
                <div className="p-4 rounded-xl bg-surface-container-lowest border-2 border-transparent peer-checked:border-primary flex flex-col items-center gap-3">
                  <span className="material-symbols-outlined text-3xl text-on-surface-variant">dark_mode</span>
                  <span className="font-semibold text-sm">深色模式</span>
                </div>
              </label>
            </div>
            <button className="px-8 py-2.5 rounded-xl font-semibold bg-primary text-white" onClick={async () => {
              const next = await api<WorkspaceSettings>('/workspace/settings', {
                method: 'PATCH',
                body: JSON.stringify({ workspace_name: workspaceName, theme }),
              });
              setSettings(next);
            }}>保存设置</button>
            {settings && <p className="text-sm text-on-surface-variant">当前：{settings.workspace_name} / {settings.theme}</p>}
          </div>
        </section>
      </main>
    </div>
  );
}

function TeamPage() {
  const [metrics, setMetrics] = useState<TeamMetrics | null>(null);
  useEffect(() => { void api<TeamMetrics>('/team/metrics').then(setMetrics); }, []);

  return (
    <div className="flex-1 lg:ml-64 pt-16 h-screen flex flex-col overflow-y-auto bg-surface">
      <div className="p-8 max-w-7xl mx-auto w-full space-y-12">
        <div>
          <h2 className="text-4xl font-extrabold tracking-tight text-on-surface font-headline mb-2">团队可用性与绩效</h2>
          <p className="text-on-surface-variant font-medium">实时资源分配与交付速度概览。</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-surface-container-low p-6 rounded-xl">
              <h3 className="text-lg font-bold font-headline mb-6">工作负载分布</h3>
              <div className="space-y-4">
                {Object.entries(metrics?.workload ?? {}).map(([name, count]) => (
                  <div key={name} className="space-y-2">
                    <div className="flex justify-between text-sm"><span className="font-semibold text-on-surface">{toZhColumn(name)}</span><span className="text-on-surface-variant">{count} 个任务</span></div>
                    <div className="h-2 w-full bg-surface-container-high rounded-full overflow-hidden"><div className="h-full bg-primary rounded-full" style={{ width: `${Math.min(100, count * 15)}%` }} /></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-surface-container-low p-6 rounded-xl h-full flex flex-col">
              <h3 className="text-lg font-bold font-headline mb-6">最近活动</h3>
              <div className="space-y-4">
                {metrics?.recent_activity.map((a) => (
                  <div key={a.id} className="bg-surface-container-lowest p-3 rounded-lg">
                    <p className="text-sm text-on-surface font-medium">{a.action}</p>
                    <p className="text-xs text-on-surface-variant">{a.details}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MobileNav() {
  const location = useLocation();
  const path = location.pathname;
  const activeClass = 'flex flex-col items-center justify-center text-[#0053db] font-bold bg-[#0053db]/5 rounded-xl px-4 py-1 group';
  const inactiveClass = 'flex flex-col items-center justify-center text-[#566166] group';

  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full flex justify-around items-center px-4 py-3 bg-white/80 backdrop-blur-md border-t border-[#a9b4b9]/15 z-50">
      <Link to="/" className={path === '/' ? activeClass : inactiveClass}><span className="material-symbols-outlined">dashboard</span><span className="text-[10px] uppercase tracking-wider font-inter mt-1">看板</span></Link>
      <Link to="/archive" className={path === '/archive' ? activeClass : inactiveClass}><span className="material-symbols-outlined">archive</span><span className="text-[10px] uppercase tracking-wider font-inter mt-1">归档</span></Link>
      <Link to="/team" className={path === '/team' ? activeClass : inactiveClass}><span className="material-symbols-outlined">group</span><span className="text-[10px] uppercase tracking-wider font-inter mt-1">团队</span></Link>
      <Link to="/settings" className={path === '/settings' ? activeClass : inactiveClass}><span className="material-symbols-outlined">menu</span><span className="text-[10px] uppercase tracking-wider font-inter mt-1">菜单</span></Link>
    </nav>
  );
}

export function App() {
  return (
    <div className="min-h-screen bg-surface">
      <TopNavBar />
      <div className="flex flex-col lg:flex-row min-h-screen">
        <SideNavBar />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/archive" element={<ArchivePage />} />
          <Route path="/team" element={<TeamPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <MobileNav />
    </div>
  );
}
