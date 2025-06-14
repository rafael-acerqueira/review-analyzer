import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "../lib/auth/authOptions";

export async function middleware(req) {
  const session = await getServerSession(authOptions);


  if (!session) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  if (req.nextUrl.pathname === '/') {
    return NextResponse.next();
  }

  if (req.nextUrl.pathname.startsWith('/admin')) {
    if (session.user?.role !== 'admin') {
      return NextResponse.redirect(new URL('/', req.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/*", "/"],
};