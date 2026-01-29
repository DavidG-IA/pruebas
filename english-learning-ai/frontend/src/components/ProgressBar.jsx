function ProgressBar({ progress }) {
  return (
    <div style={styles.container}>
      <div style={{ ...styles.fill, width: `${progress}%` }} />
    </div>
  )
}

const styles = {
  container: {
    background: '#e2e8f0',
    height: '8px',
    borderRadius: '4px',
    overflow: 'hidden'
  },
  fill: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    height: '100%',
    transition: 'width 0.3s ease'
  }
}

export default ProgressBar
