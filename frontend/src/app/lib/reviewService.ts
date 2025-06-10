export type ReviewPayload = {
  text: string
}

export type Review = {
  text: string,
  corrected_text?: string,
  sentiment: string,
  status: string,
  feedback: string,
  suggestion?: string
}

export async function submitReviewRequest(payload: ReviewPayload) {
  const response = await fetch("/api/submit-review-proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error("Error when analyze the review")
  return response.json()
}

export async function createReview(payload: Review) {
  const response = await fetch("/api/create-review-proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error("We got an error during the review store")
  return response.json()
}

export async function listReview(filters: Record<string, string> = {}, token: string) {
  const query = new URLSearchParams(filters).toString()
  const response = await fetch(`/api/list-review-proxy?${query}`, {
    method: "GET",
    headers: { "Content-Type": "application/json", 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error("We got an error listing the reviews")
  return response.json()
}

export async function deleteReview(id: number, token: string) {
  const response = await fetch(`/api/delete-review-proxy/${id}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json", 'Authorization': `Bearer ${token}` },
  })
  if (!response.ok) throw new Error("We got an error listings the reviews")
  return response.json()
}