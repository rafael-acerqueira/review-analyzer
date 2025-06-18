import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const body = await req.json()
  const apiUrl = process.env.API_URL

  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    console.log('Status:', response.status);

    const data = await response.json()

    console.log('Body:', data);
    return NextResponse.json(data, { status: response.status })

  } catch (error) {
    console.error('[Register Proxy Error]', error)
    return NextResponse.json({ detail: 'Internal error' }, { status: 500 })
  }
}