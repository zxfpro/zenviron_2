export type Role = 'admin' | 'product' | 'developer' | 'tester';
export type Priority = 'low' | 'normal' | 'high' | 'urgent';
export type ArchiveState = 'active' | 'archived';

export interface TaskContract {
  id: number;
  code: string;
  title: string;
  description: string;
  priority: Priority;
  archived: boolean;
  column_id: number;
  assignee_id: number | null;
}
