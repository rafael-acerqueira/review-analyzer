import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import { AuthOptions } from 'next-auth'

function getApiBaseUrl() {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  );
}

export const authOptions: AuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'text' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        const url = `${getApiBaseUrl()}/api/v1/auth/login`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(credentials),
        });

        if (!res.ok) {
          console.error("[Credentials Login Error]", await res.text());
          return null;
        }

        const ctype = res.headers.get("content-type") || "";
        if (!ctype.includes("application/json")) {
          console.error("[Credentials Login Error] Not JSON:", await res.text());
          return null;
        }

        const user = await res.json();
        if (!user) return null;
        return user;
      }
    })
  ],

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.user = user;
        if ("access_token" in user) token.access_token = user.access_token;
        if ("refresh_token" in user) token.refresh_token = user.refresh_token;
        if (user?.role) token.user.role = user.role;
      }
      return token;
    },

    async session({ session, token }) {
      if (token?.user) session.user = token.user as any;
      if (token?.access_token) (session as any).access_token = token.access_token;
      if (token?.refresh_token) (session as any).refresh_token = token.refresh_token;
      return session;
    },

    async signIn({ account, profile }) {
      return true;
    },
  },

  events: {
    async signIn({ account, profile }) {
      try {
        if (account?.provider === "google" && profile?.email) {
          const url = `${getApiBaseUrl()}/api/v1/auth/google`;
          const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: profile.email,
              sub: (profile as any).sub,
            }),
          });

          if (!res.ok && res.status !== 409) {
            console.error("[events.signIn] upsert google falhou", res.status, await res.text());
          }
        }
      } catch (e) {
        console.error("[events.signIn] exceção no upsert google", e);
      }
    },
  },


  pages: {
    signIn: '/auth/login',
    error: '/auth/login',
  },

  session: {
    strategy: 'jwt',
  },

  secret: process.env.NEXTAUTH_SECRET,
}