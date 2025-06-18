import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const body = await req.json();

  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    return NextResponse.json(
      { detail: 'API_URL is not configured in environment variables.' },
      { status: 500 }
    );
  }

  const token = req.headers.get('authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json(
      { detail: 'Authentication token missing.' },
      { status: 401 }
    );
  }

  try {
    const response = await fetch(`${apiUrl}/api/v1/analyze_review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
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
