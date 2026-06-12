import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';
import { authOptions } from './auth/authOptions';

type BackendFetchOptions = {
  method?: string;
  body?: unknown;
};

type SessionWithBackendToken = {
  access_token?: string;
};

async function parseBackendResponse(response: Response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }
  return { detail: 'Unexpected response format from backend.' };
}

export async function backendFetch(path: string, options: BackendFetchOptions = {}) {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    return NextResponse.json(
      { detail: 'API_URL is not configured in environment variables.' },
      { status: 500 }
    );
  }

  const session = await getServerSession(authOptions);
  const accessToken = (session as SessionWithBackendToken | null)?.access_token;

  if (!accessToken) {
    return NextResponse.json({ detail: 'Not authenticated' }, { status: 401 });
  }

  try {
    const response = await fetch(`${apiUrl}${path}`, {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });

    const data = await parseBackendResponse(response);
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
