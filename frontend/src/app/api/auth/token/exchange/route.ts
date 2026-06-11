import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const body = await req.json();

  const apiUrl = process.env.API_URL;
  const internalAuthSecret = process.env.INTERNAL_AUTH_SECRET || process.env.NEXTAUTH_SECRET;

  if (!apiUrl || !internalAuthSecret) {
    return NextResponse.json(
      { detail: 'API auth environment is not configured.' },
      { status: 500 }
    );
  }


  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/token/exchange`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Internal-Auth': internalAuthSecret,
      },
      body: JSON.stringify(body),
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
