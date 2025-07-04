import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import { AuthOptions } from 'next-auth'

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
    async jwt({ token, user }) {
      if (user) {
        token.user = user
        token.access_token = user.access_token;
        token.refresh_token = user.refresh_token

        if (user.role) token.user.role = user.role
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