import { useState } from 'react'
import ExerciseSetup from '../components/ExerciseSetup'
import ListeningExercise from '../components/ListeningExercise'
import Results from '../components/Results'
import { generateExercise } from '../services/api'

function Listening() {
  const [state, setState] = useState('setup') // 'setup', 'loading', 'exercise', 'results'
  const [exerciseData, setExerciseData] = useState(null)
  const [results, setResults] = useState(null)

  const handleGenerate = async (formData) => {
    setState('loading')
    try {
      const data = await generateExercise(formData)
      setExerciseData(data)
      setState('exercise')
    } catch (error) {
      console.error(error)
      alert('Error al generar ejercicio. Verifica tu conexión.')
      setState('setup')
    }
  }

  const handleComplete = (score) => {
    setResults(score)
    setState('results')
  }

  const handleRetry = () => {
    setState('setup')
    setExerciseData(null)
    setResults(null)
  }

  return (
    <div>
      <h1>🎧 Listening Practice</h1>

      {state === 'setup' && (
        <ExerciseSetup onGenerate={handleGenerate} exerciseType="listening" />
      )}

      {state === 'loading' && (
        <div className="card loading">
          <div className="spinner" />
          <p>La IA está generando tu práctica personalizada...</p>
        </div>
      )}

      {state === 'exercise' && exerciseData && (
        <ListeningExercise data={exerciseData} onComplete={handleComplete} />
      )}

      {state === 'results' && results && (
        <Results
          score={results.score}
          total={results.total}
          onRetry={handleRetry}
        />
      )}
    </div>
  )
}

export default Listening
