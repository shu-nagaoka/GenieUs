import NextAuth, { DefaultSession } from 'next-auth'

declare module 'next-auth' {
  interface Session {
    accessToken?: string
    idToken?: string
    user: {
      id?: string
      name?: string
      email?: string
      image?: string
    } & DefaultSession['user']
  }

  interface JWT {
    accessToken?: string
    idToken?: string
    user?: any
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken?: string
    idToken?: string
    user?: any
  }
}