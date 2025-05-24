import React, { useState, useEffect, useRef } from 'react';
import Layout from '@theme/Layout';
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import html2canvas from 'html2canvas';
import * as d3 from 'd3';

function getColor(index) {
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#d0ed57', '#a4de6c', '#8dd1e1', '#83a6ed'
  ];
  return colors[index % colors.length];
}

export default function GraphPage() {
  const [allData, setAllData] = useState([]);
  const [selectedIdPCS, setSelectedIdPCS] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('All');
  const [selectedAngle, setSelectedAngle] = useState('All');
  const [selectedDistance, setSelectedDistance] = useState('All');
  const [temperatureFilter, setTemperatureFilter] = useState(25);
  const [selectedMetric, setSelectedMetric] = useState('Delta_ht');
  const chartRef = useRef();

  useEffect(() => {
    d3.csv('/data/delta_results.csv').then(rawData => {
      const expanded = [];
      rawData.forEach(row => {
        const baseInfo = {};
        for (const [key, value] of Object.entries(row)) {
          baseInfo[key] = isNaN(+value) || key.startsWith('Delta_') ? value : +value;
        }
        for (const key in row) {
          if ((key.startsWith('Delta_ht_') || key.startsWith('Delta_P_') || key.startsWith('Delta_Teq_')) && row[key] !== '') {
            const metric = key.split('_')[1];
            const metricKey = `Delta_${metric}`;
            expanded.push({
              ...baseInfo,
              BodyPart: key.replace(/^Delta_.*?_/, '').trim(),
              [metricKey]: +row[key],
              Level: row.Level.trim()
            });
          }
        }
      });
      setAllData(expanded);
    });
  }, []);

  const uniqueIdPCS = Array.from(new Set(allData.map(row => `${row.ID} - ${row.PCS_name}`)));
  const currentPCSData = selectedIdPCS === '' ? [] : allData.filter(d => `${d.ID} - ${d.PCS_name}` === selectedIdPCS);
  const uniqueLevels = Array.from(new Set(currentPCSData.map(row => row.Level)));
  const uniqueAngles = Array.from(new Set(currentPCSData.map(row => row.Angle)));
  const uniqueDistances = Array.from(new Set(currentPCSData.map(row => row.Distance)));

  const filteredData = currentPCSData.filter(d => {
    const matchesLevel = selectedLevel === 'All' || d.Level === selectedLevel;
    const matchesAngle = selectedAngle === 'All' || d.Angle === Number(selectedAngle);
    const matchesDistance = selectedDistance === 'All' || d.Distance === Number(selectedDistance);
    const matchesTemp = Number(d.Tset) === temperatureFilter;
    return matchesLevel && matchesAngle && matchesDistance && matchesTemp && d[selectedMetric] !== undefined;
  });

  const groupedByLevel = filteredData.reduce((acc, cur) => {
    if (!acc[cur.Level]) acc[cur.Level] = [];
    acc[cur.Level].push(cur);
    return acc;
  }, {});

  const downloadCSV = () => {
    const headers = ['BodyPart', 'Level', 'Angle', 'Distance', 'Tset', selectedMetric];
    const rows = filteredData.map(row => headers.map(h => row[h]));
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${selectedMetric}_data.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadImage = () => {
    if (!chartRef.current) return;
    html2canvas(chartRef.current).then(canvas => {
      const link = document.createElement('a');
      link.download = `${selectedMetric}_graph.png`;
      link.href = canvas.toDataURL();
      link.click();
    });
  };

  return (
    <Layout title="PCS Graph" description="Filter by PCS and Level">
      <main style={{ padding: '2rem' }}>
        <h1 style={{ textAlign: 'center' }}>{selectedMetric} by Body Part</h1>

        <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
          <label>ID & PCS: </label>
          <select value={selectedIdPCS} onChange={e => setSelectedIdPCS(e.target.value)}>
            <option value="" disabled hidden>Select a PCS</option>
            {uniqueIdPCS.map(val => <option key={val} value={val}>{val}</option>)}
          </select>
          <label style={{ marginLeft: '1rem' }}>Level: </label>
          <select value={selectedLevel} onChange={e => setSelectedLevel(e.target.value)}>
            <option value="All">All</option>
            {uniqueLevels.map(val => <option key={val} value={val}>{val}</option>)}
          </select>
          <label style={{ marginLeft: '1rem' }}>Angle: </label>
          <select value={selectedAngle} onChange={e => setSelectedAngle(e.target.value)}>
            <option value="All">All</option>
            {uniqueAngles.map(val => <option key={val} value={val}>{val}</option>)}
          </select>
          <label style={{ marginLeft: '1rem' }}>Distance: </label>
          <select value={selectedDistance} onChange={e => setSelectedDistance(e.target.value)}>
            <option value="All">All</option>
            {uniqueDistances.map(val => <option key={val} value={val}>{val}</option>)}
          </select>
          <label style={{ marginLeft: '1rem' }}>Result: </label>
          <select value={selectedMetric} onChange={e => setSelectedMetric(e.target.value)}>
            <option value="Delta_ht">Delta_ht</option>
            <option value="Delta_P">Delta_P</option>
            <option value="Delta_Teq">Delta_Teq</option>
          </select>
          <button style={{ marginLeft: '2rem' }} onClick={downloadCSV}>Download CSV</button>
          <button style={{ marginLeft: '1rem' }} onClick={downloadImage}>Download Image</button>
        </div>

        <div ref={chartRef} style={{ width: '100%', height: 400 }}>
          <ResponsiveContainer>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="BodyPart" type="category" interval={0} allowDuplicatedCategory={false} angle={-45} textAnchor="end" height={70} />
              <YAxis label={{ value: selectedMetric, angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend layout="horizontal" verticalAlign="top" align="center" />
              {Object.entries(groupedByLevel).map(([level, data], index) => (
                <Line
                  key={level}
                  data={data}
                  type="monotone"
                  dataKey={selectedMetric}
                  name={`Level ${level}`}
                  stroke={getColor(index)}
                  dot={{ r: 2 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </main>
    </Layout>
  );
}
