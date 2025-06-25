import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/app/api/auth/[...nextauth]/route'

export function getServerAuthSession() {
  return getServerSession(authOptions)
}

// Client-side auth utilities
export const signIn = (provider?: string) => {
  return import('next-auth/react').then(({ signIn }) => signIn(provider))
}

export const signOut = () => {
  return import('next-auth/react').then(({ signOut }) => signOut())
}

// Token validation utility for API calls
export async function validateGoogleToken(token: string): Promise<any> {
  try {
    const response = await fetch(
      `https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${token}`
    )
    
    if (!response.ok) {
      throw new Error('Token validation failed')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Token validation error:', error)
    throw new Error('Invalid token')
  }
}

// API call with authentication
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {},
  token?: string
) {
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  }

  return fetch(url, {
    ...options,
    headers,
  })
}