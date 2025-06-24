import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export function StatusBar({ by_status }: { by_status: Record<string, number> }) {
  const chartData = Object.entries(by_status).map(([name, value]) => ({
    status: name,
    count: value
  }))

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow w-full flex flex-col items-center">
      <span className="mb-2 font-semibold">Reviews by Status</span>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={chartData}>
          <XAxis dataKey="status" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
