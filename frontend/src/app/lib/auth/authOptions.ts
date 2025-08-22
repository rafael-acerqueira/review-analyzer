import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import { AuthOptions } from 'next-auth'

type RefreshResponse = {
  access_token: string;
  refresh_token: string;
  expires_in?: number;
  token_type?: string;
};

function decodeExpMs(jwt: string | undefined): number | null {
  if (!jwt) return null;
  try {
    const [, payloadB64] = jwt.split(".");
    const json = JSON.parse(Buffer.from(payloadB64, "base64").toString("utf8"));
    return typeof json?.exp === "number" ? json.exp * 1000 : null;
  } catch {
    return null;
  }
}
function aboutToExpire(expMs: number | null, skewMs = 60_000) {
  if (!expMs) return true;
  return Date.now() >= expMs - skewMs;
}

async function refreshWithBackend(refreshToken: string): Promise<RefreshResponse> {
  const apiUrl = process.env.API_URL!;
  const res = await fetch(`${apiUrl}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) throw new Error("Refresh failed");
  return res.json();
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
        const res = await fetch(`${process.env.NEXTAUTH_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials)
        })

        const user = await res.json()
        if (!res.ok || !user) {
          return null
        }

        return user
      }
    })
  ],

  callbacks: {
    async jwt({ token, user, account, profile }) {
      if (user) {
        token.user = user
        token.access_token = user.access_token;
        token.refresh_token = user.refresh_token
        token.access_token_exp = decodeExpMs((user as any).access_token)

        if (user.role) token.user.role = user.role
      }

      const expMs = (token as any).access_token_exp as number | null;
      const refresh = (token as any).refresh_token as string | undefined;

      if (aboutToExpire(expMs) && refresh) {
        try {
          const refreshed = await refreshWithBackend(refresh);
          (token as any).access_token = refreshed.access_token;
          (token as any).refresh_token = refreshed.refresh_token;
          (token as any).access_token_exp = decodeExpMs(refreshed.access_token);
        } catch (e) {
          console.error("[jwt] refresh failed", e);
        }
      }

      if (account?.provider === "google" && profile?.email) {
        const sub =
          (account as any)?.providerAccountId ??
          (profile as any)?.sub ??
          null;

        if (sub) {
          try {
            const res = await fetch(`${process.env.NEXTAUTH_URL}/api/auth/token/exchange`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email: profile.email, sub }),
            });

            if (res.ok) {
              const ctype = res.headers.get("content-type") || "";
              const data = ctype.includes("application/json") ? await res.json() : null;
              if (data?.access_token) {
                (token as any).access_token = data.access_token;
                (token as any).access_token_exp = decodeExpMs(data.access_token);
                if (data.refresh_token) (token as any).refresh_token = data.refresh_token;
              }
            } else {
              const msg = await res.text();
              console.error("[jwt] token-exchange failed", res.status, msg);
            }
          } catch (e) {
            console.error("[jwt] token-exchange exception", e);
          }
        }
      }
      return token
    },

    async session({ session, token }) {
      session.user = token.user
      session.access_token = token.access_token;
      session.refresh_token = token.refresh_token;
      return session
    },

    async signIn({ account, profile }) {
      if (account?.provider === 'google' && profile?.email) {
        try {
          const res = await fetch(`${process.env.NEXTAUTH_URL}/api/auth/google`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: profile.email,
              sub: profile.sub,
            }),
          })

          if (!res.ok) {
            console.error('[Google Register Error]', await res.text())
            return false
          }

          return true
        } catch (error) {
          console.error('[Google SignIn Exception]', error)
          return false
        }
      }

      return true
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