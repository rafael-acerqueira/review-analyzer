import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'

const COLORS = ['#16a34a', '#f59e42', '#dc2626'] // verde, laranja, vermelho

export function SentimentPie({ by_sentiment }: { by_sentiment: Record<string, number> }) {
  const chartData = Object.entries(by_sentiment).map(([name, value]) => ({
    name, value
  }))

  return (
    <div className="flex w-full flex-col border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <span className="border-b border-slate-200 px-5 py-4 text-base font-semibold dark:border-slate-800">Reviews by Sentiment</span>
      <div className="flex justify-center p-4">
      <PieChart width={340} height={240}>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          label
        >
          {chartData.map((entry, idx) => (
            <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
      </div>
    </div>
  )
}
