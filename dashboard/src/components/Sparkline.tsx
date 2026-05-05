import { Line, LineChart, ResponsiveContainer } from 'recharts';

export function Sparkline({
  data,
  color = '#ff6b00',
  height = 60,
}: {
  data: Array<{ date: string; count: number }>;
  color?: string;
  height?: number;
}) {
  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
          <Line
            type="monotone"
            dataKey="count"
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
