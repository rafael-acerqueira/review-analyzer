'use client'

export default function ReviewForm() {

  return (
    <div className="max-w-lg mx-auto p-4 bg-white shadow rounded-xl space-y-4">
      <h1 className="text-xl font-bold">Client Review</h1>
      <form onSubmit={() => { }} className="space-y-4">
        <textarea
          className="w-full border rounded p-2"
          placeholder="Tell me your thoughts"
          rows={5}
          required
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Enviar
        </button>


      </form>
    </div>
  )
}