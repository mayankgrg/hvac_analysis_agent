export function ReasoningPanel({ reasoning }: { reasoning: any }) {
  return (
    <div style={{ borderTop: "1px solid var(--line)", paddingTop: 8, marginTop: 8 }}>
      <p><strong>Root cause:</strong> {reasoning.root_cause}</p>
      <p><strong>Recoverable amount:</strong> ${reasoning.recoverable_amount?.toLocaleString()}</p>
      <p><strong>Confidence:</strong> {(reasoning.confidence * 100).toFixed(0)}%</p>
      <ul>
        {reasoning.recovery_actions?.map((a: any, idx: number) => (
          <li key={idx}>{a.action} ({a.owner}) - ${a.amount?.toLocaleString()}</li>
        ))}
      </ul>
    </div>
  );
}
