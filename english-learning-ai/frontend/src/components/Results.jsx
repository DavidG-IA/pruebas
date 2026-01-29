function Results({ score, total, onRetry }) {
  const percentage = (score / total) * 100

  let feedback = ''
  let emoji = ''

  if (percentage >= 90) {
    feedback = '¡Excelente! Dominas este tema.'
    emoji = '🌟'
  } else if (percentage >= 70) {
    feedback = '¡Muy bien! Vas por buen camino.'
    emoji = '👏'
  } else if (percentage >= 50) {
    feedback = 'Bien hecho. Sigue practicando.'
    emoji = '👍'
  } else {
    feedback = 'No te desanimes. La práctica hace al maestro.'
    emoji = '💪'
  }

  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <h2>🎉 ¡Práctica Completada!</h2>

      <div style={styles.score}>
        {score}/{total}
      </div>

      <div style={styles.feedback}>
        {emoji} {feedback}
      </div>

      <div style={styles.percentage}>
        {percentage.toFixed(0)}% correcto
      </div>

      <button onClick={onRetry} className="btn btn-primary" style={{ marginTop: '2rem' }}>
        🔄 Generar Nueva Práctica
      </button>
    </div>
  )
}

const styles = {
  score: {
    fontSize: '4rem',
    fontWeight: 'bold',
    color: '#667eea',
    margin: '2rem 0'
  },
  feedback: {
    fontSize: '1.5rem',
    color: '#2d3748',
    margin: '1rem 0'
  },
  percentage: {
    fontSize: '1.25rem',
    color: '#718096'
  }
}

export default Results
