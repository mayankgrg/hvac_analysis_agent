export function DossierHeader({ dossier }: { dossier: any }) {
  const f = dossier.financials;
  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <h2 style={{ marginTop: 0 }}>{dossier.name}</h2>
      <div className="grid" style={{ gridTemplateColumns: "repeat(4, minmax(140px,1fr))" }}>
        <div><div>Health</div><strong>{dossier.health_score.toFixed(1)}</strong></div>
        <div><div>Bid Margin</div><strong>{(f.bid_margin_pct * 100).toFixed(1)}%</strong></div>
        <div><div>Realized Margin</div><strong>{(f.realized_margin_pct * 100).toFixed(1)}%</strong></div>
        <div><div>Erosion</div><strong>{(f.margin_erosion_pct * 100).toFixed(1)}%</strong></div>
      </div>
    </div>
  );
}
