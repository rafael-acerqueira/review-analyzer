import { backendFetch } from '@/app/lib/backendFetch';
import { NextRequest } from 'next/server';

export async function GET(req: NextRequest) {
  const searchParams = req.nextUrl.searchParams
  return backendFetch(`/api/v1/admin/reviews?${searchParams.toString()}`);
}
