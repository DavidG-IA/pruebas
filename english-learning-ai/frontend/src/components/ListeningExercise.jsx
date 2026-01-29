import { useState } from 'react'
import { Volume2, ChevronLeft, ChevronRight } from 'lucide-react'
import ProgressBar from './ProgressBar'

function ListeningExercise({ data, onComplete }) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState(Array(data.questions.length).fill(null))

  const question = data.questions[currentQuestion]

  const handleAnswer = (answer) => {
    const newAnswers = [...answers]
    newAnswers[currentQuestion] = answer
    setAnswers(newAnswers)
  }

  const playAudio = () => {
    const audio = new Audio(question.audio_url)
    audio.play()
  }

  const handleNext = () => {
    if (currentQuestion < data.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = () => {
    let correct = 0
    data.questions.forEach((q, idx) => {
      if (answers[idx] === q.correct) correct++
    })
    onComplete({ score: correct, total: data.questions.length })
  }

  const progress = ((currentQuestion + 1) / data.questions.length) * 100

  return (
    <div className="card">
      <ProgressBar progress={progress} />

      <div style={{ marginTop: '2rem' }}>
        <div style={{ marginBottom: '1rem', color: '#667eea', fontWeight: 'bold' }}>
          Pregunta {currentQuestion + 1} de {data.questions.length}
        </div>

        <div style={styles.audioPlayer}>
          <button onClick={playAudio} style={styles.playButton}>
            <Volume2 size={24} />
          </button>
          <div>
            <div style={{ fontWeight: 600 }}>Escucha el audio</div>
            <div style={{ fontSize: '0.9rem', color: '#718096' }}>
              Haz clic para reproducir
            </div>
          </div>
        </div>

        <div style={styles.question}>
          {question.question}
        </div>

        <div style={{ marginTop: '1.5rem' }}>
          {question.options.map((option, idx) => (
            <div
              key={idx}
              onClick={() => handleAnswer(String.fromCharCode(97 + idx))}
              style={{
                ...styles.option,
                ...(answers[currentQuestion] === String.fromCharCode(97 + idx) ? styles.optionSelected : {})
              }}
            >
              {String.fromCharCode(97 + idx)}) {option}
            </div>
          ))}
        </div>

        <div style={styles.navigation}>
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className="btn btn-secondary"
          >
            <ChevronLeft size={20} /> Anterior
          </button>

          {currentQuestion === data.questions.length - 1 ? (
            <button onClick={handleSubmit} className="btn btn-primary">
              ✅ Terminar
            </button>
          ) : (
            <button onClick={handleNext} className="btn btn-primary">
              Siguiente <ChevronRight size={20} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  audioPlayer: {
    background: '#f7fafc',
    padding: '1.5rem',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    margin: '1.5rem 0'
  },
  playButton: {
    background: '#667eea',
    color: 'white',
    border: 'none',
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'transform 0.2s'
  },
  question: {
    fontSize: '1.25rem',
    fontWeight: '500',
    margin: '1.5rem 0'
  },
  option: {
    background: 'white',
    padding: '1rem',
    margin: '0.75rem 0',
    borderRadius: '8px',
    border: '2px solid #e2e8f0',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  optionSelected: {
    background: '#667eea',
    color: 'white',
    borderColor: '#667eea'
  },
  navigation: {
    display: 'flex',
    gap: '1rem',
    marginTop: '2rem'
  }
}

export default ListeningExercise
