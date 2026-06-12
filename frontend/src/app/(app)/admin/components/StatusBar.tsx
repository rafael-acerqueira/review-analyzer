import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export function StatusBar({ by_status }: { by_status: Record<string, number> }) {
  const chartData = Object.entries(by_status).map(([name, value]) => ({
    status: name,
    count: value
  }))

  return (
    <div className="flex w-full flex-col border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <span className="border-b border-slate-200 px-5 py-4 text-base font-semibold dark:border-slate-800">Reviews by Status</span>
      <div className="p-4">
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
    </div>
  )
}
