import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const body = await req.json();

  try {
    const response = await fetch(`${process.env.API_URL}/api/v1/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });

  } catch (error: any) {
    return NextResponse.json({ detail: 'Internal FastAPI Server Error.' }, { status: 500 });
  }
}