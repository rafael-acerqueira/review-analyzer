import NextAuth, { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      email: string;
      name?: string;
      role?: string;
      access_token?: string;
      refresh_token?: string;
    };
    access_token?: string;
    refresh_token?: string;
  }

  interface User {
    id: string;
    email: string;
    name?: string;
    role?: string;
    access_token?: string;
    refresh_token?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    user: {
      id: string;
      email: string;
      name?: string;
      role?: string;
    };
    access_token?: string;
    refresh_token?: string;
  }
}