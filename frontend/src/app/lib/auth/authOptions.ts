import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import { AuthOptions } from 'next-auth'

function getApiBaseUrl() {
  return (
    process.env.NEXTAUTH_URL ||
    "http://localhost:3000"
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
        const url = getApiBaseUrl() + "/api/auth/login";
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
      if (account?.provider === "google" && profile?.email) {
        const url = getApiBaseUrl() + "/api/auth/google";
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: profile.email, sub: profile.sub }),
        });

        if (!res.ok) {
          const t = await res.text();
          console.error("[Google Register Error]", t);
          return false;
        }
        return true;
      }
      return true;
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