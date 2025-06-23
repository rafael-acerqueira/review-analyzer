import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'

const COLORS = ['#16a34a', '#f59e42', '#dc2626'] // verde, laranja, vermelho

export function SentimentPie({ by_sentiment }: { by_sentiment: Record<string, number> }) {
  const chartData = Object.entries(by_sentiment).map(([name, value]) => ({
    name, value
  }))

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow w-full flex flex-col items-center mb-8">
      <span className="mb-2 font-semibold">Reviews by Sentiment</span>
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
  )
}
