import { useState } from 'react'
import ExerciseSetup from '../components/ExerciseSetup'
import SpeakingExercise from '../components/SpeakingExercise'
import { generateExercise } from '../services/api'

function Speaking() {
  const [state, setState] = useState('setup')
  const [exerciseData, setExerciseData] = useState(null)

  const handleGenerate = async (formData) => {
    setState('loading')
    try {
      const data = await generateExercise(formData)
      setExerciseData(data)
      setState('exercise')
    } catch (error) {
      console.error(error)
      alert('Error al generar ejercicio')
      setState('setup')
    }
  }

  return (
    <div>
      <h1>🎤 Speaking Practice</h1>

      {state === 'setup' && (
        <ExerciseSetup onGenerate={handleGenerate} exerciseType="speaking" />
      )}

      {state === 'loading' && (
        <div className="card loading">
          <div className="spinner" />
          <p>Generando ejercicios de speaking...</p>
        </div>
      )}

      {state === 'exercise' && exerciseData && (
        <SpeakingExercise data={exerciseData} />
      )}
    </div>
  )
}

export default Speaking
