import React from 'react';
import Layout from '@theme/Layout';
import styles from './datasets.module.css';

const datasets = [
  {
    id: 1,
    title: 'Desk Fan - Angled',
    image: '/img/pcs_images/ID1_desk_fan_angled.png',
    fallbackImage: '/img/pcs_images/ID1_desk_fan_front.png',
    location: 'Japan',
    manufacturer: 'SilentPro',
    type: 'Cooling',
    notes: 'Personal desk fan with adjustable angle.'
  },
  {
    id: 2,
    title: 'Standing Fan - Front',
    image: '/img/pcs_images/ID2_standing_fan_angled.png',
    fallbackImage: '/img/pcs_images/ID2_standing_fan_front.png',
    location: 'Australia',
    manufacturer: 'CoolBreeze',
    type: 'Cooling',
    notes: 'Tall fan suitable for full-body cooling.'
  },
];

export default function DatasetList() {
  return (
    <Layout title="PCS Dataset List" description="Overview of PCS datasets">
      <main className={styles.container}>
        <h1>PCS Dataset List</h1>
        <div className={styles.cardGrid}>
          {datasets.map(ds => (
            <div key={ds.id} className={styles.card}>
              <img
                src={ds.image}
                alt={ds.title}
                onError={(e) => ds.fallbackImage && (e.target.src = ds.fallbackImage)}
                className={styles.cardImage}
              />
              <h3>{ds.title}</h3>
              <p><strong>Location:</strong> {ds.location}</p>
              <p><strong>Manufacturer:</strong> {ds.manufacturer}</p>
              <p><strong>Type:</strong> {ds.type}</p>
              <p>{ds.notes}</p>
            </div>
          ))}
        </div>
      </main>
    </Layout>
  );
}
