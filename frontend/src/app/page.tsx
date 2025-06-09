'use client'

import { useSession } from "next-auth/react";
import ReviewForm from "./review/components/ReviewForm";
import { useRouter } from 'next/navigation'
import { useEffect } from "react";

export default function Home() {

  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  if (status === 'loading') return <p>Loading...</p>

  return (
    <ReviewForm />
  );
}
