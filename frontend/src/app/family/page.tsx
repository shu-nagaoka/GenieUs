'use client'

import FamilyPageNew from '@/components/features/family/family-page-new'
import { AuthCheck } from '@/components/features/auth/auth-check'

export default function FamilyPage() {
  return (
    <AuthCheck>
      <FamilyPageNew />
    </AuthCheck>
  )
}