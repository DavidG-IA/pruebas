import { useState } from 'react'
import { Mic, StopCircle } from 'lucide-react'

function SpeakingExercise({ data, onComplete }) {
  const [isRecording, setIsRecording] = useState(false)
  const [currentExercise, setCurrentExercise] = useState(0)

  const exercise = data.exercises[currentExercise]

  const handleRecord = () => {
    setIsRecording(!isRecording)
    // Implementar grabación real aquí
  }

  return (
    <div className="card">
      <h3>Ejercicio {currentExercise + 1} de {data.exercises.length}</h3>

      <div style={styles.context}>
        {exercise.context}
      </div>

      <div style={styles.target}>
        <strong>Frase modelo:</strong> "{exercise.target_phrase}"
      </div>

      <button
        onClick={handleRecord}
        style={{
          ...styles.recordButton,
          background: isRecording ? '#f44336' : '#667eea'
        }}
      >
        {isRecording ? <StopCircle size={32} /> : <Mic size={32} />}
        <span>{isRecording ? 'Detener' : 'Grabar'}</span>
      </button>
    </div>
  )
}

const styles = {
  context: {
    background: '#f7fafc',
    padding: '1.5rem',
    borderRadius: '8px',
    margin: '1.5rem 0',
    fontSize: '1.1rem'
  },
  target: {
    padding: '1rem',
    margin: '1rem 0',
    fontSize: '1.1rem'
  },
  recordButton: {
    border: 'none',
    color: 'white',
    padding: '1.5rem 3rem',
    borderRadius: '50px',
    fontSize: '1.1rem',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    margin: '2rem auto',
    transition: 'transform 0.2s'
  }
}

export default SpeakingExercise
