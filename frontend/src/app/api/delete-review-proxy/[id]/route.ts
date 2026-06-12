import { backendFetch } from '@/app/lib/backendFetch';
import { NextRequest, NextResponse } from 'next/server';

type DeleteReviewContext = {
  params: Promise<{
    id: string;
  }>;
};

export async function DELETE(_req: NextRequest, context: DeleteReviewContext) {
  const { id } = await context.params

  if (!id) {
    return NextResponse.json(
      { detail: 'Missing "id" in request path.' },
      { status: 400 }
    );
  }

  return backendFetch(`/api/v1/admin/reviews/${id}`, { method: 'DELETE' });
}
