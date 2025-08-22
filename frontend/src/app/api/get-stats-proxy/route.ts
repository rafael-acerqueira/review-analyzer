import { authOptions } from '@/app/lib/auth/authOptions';
import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';

export async function GET() {

  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    return NextResponse.json(
      { detail: 'API_URL is not configured in environment variables.' },
      { status: 500 }
    );
  }

  const session = await getServerSession(authOptions);
  const accessToken = (session as any)?.access_token;

  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  try {
    const response = await fetch(`${apiUrl}/api/v1/admin/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
    });

    const contentType = response.headers.get('content-type');

    let data;
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = { detail: 'Unexpected response format from backend.' };
    }

    return NextResponse.json(data, { status: response.status });

  } catch (error: unknown) {
    console.error('[Proxy Error]', error);
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { detail: `Internal FastAPI Server Error: ${message}` },
      { status: 500 }
    );
  }
}
