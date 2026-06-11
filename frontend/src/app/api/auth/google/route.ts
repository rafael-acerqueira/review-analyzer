import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const apiUrl = process.env.API_URL
  const internalAuthSecret = process.env.INTERNAL_AUTH_SECRET || process.env.NEXTAUTH_SECRET

  if (!apiUrl || !internalAuthSecret) {
    return NextResponse.json(
      { detail: 'API auth environment is not configured.' },
      { status: 500 }
    )
  }

  const body = await req.json()

  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Internal-Auth': internalAuthSecret,
      },
      body: JSON.stringify(body),
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error: unknown) {
    console.error('[Proxy Error] Google Login:', error)
    const message = error instanceof Error ? error.message : 'Unknown error'
    return NextResponse.json({ detail: message }, { status: 500 })
  }
}
