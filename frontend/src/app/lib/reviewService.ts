export type ReviewPayload = {
  text: string
}

export async function submitReviewRequest(payload: ReviewPayload) {
  const response = await fetch("/api/submit-review-proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error("Erro ao enviar review")
  return response.json()
}