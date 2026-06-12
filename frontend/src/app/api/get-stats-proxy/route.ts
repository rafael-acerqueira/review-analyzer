import { backendFetch } from '@/app/lib/backendFetch';

export async function GET() {
  return backendFetch('/api/v1/admin/stats');
}
