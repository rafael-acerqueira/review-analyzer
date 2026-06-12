import { backendFetch } from '@/app/lib/backendFetch';
import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  const body = await req.json();
  return backendFetch('/api/v1/reviews', { method: 'POST', body });
}
