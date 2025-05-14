import React, { useState } from 'react';
import Layout from '@theme/Layout';
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';

// サンプルデータ
const allData = [
  { category: 'Cooling', name: 'Jan', value: 30 },
  { category: 'Cooling', name: 'Feb', value: 50 },
  { category: 'Heating', name: 'Mar', value: 40 },
  { category: 'Cooling', name: 'Apr', value: 80 },
  { category: 'Heating', name: 'May', value: 20 }
];

export default function GraphPage() {
  const [filter, setFilter] = useState('All');

  const filteredData = allData.filter(d => {
    if (filter === 'All') return true;
    return d.category === filter;
  });

  return (
    <Layout title="Graph Page" description="Interactive graph with filtering">
      <main style={{ padding: '2rem' }}>
        <h1 style={{ textAlign: 'center' }}>PCS Sample Graph</h1>

        {/* フィルター選択 */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <label style={{ marginRight: '1rem' }}>Filter by Category:</label>
          <select value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="All">All</option>
            <option value="Cooling">Cooling</option>
            <option value="Heating">Heating</option>
          </select>
        </div>

        {/* グラフ */}
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <LineChart width={600} height={300} data={filteredData}>
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
          </LineChart>
        </div>
      </main>
    </Layout>
  );
}
