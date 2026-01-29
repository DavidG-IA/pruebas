import { useState } from 'react'

function ExerciseSetup({ onGenerate, exerciseType = 'listening' }) {
  const [formData, setFormData] = useState({
    level: 'A1',
    topic: '',
    num_questions: 10
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onGenerate({ ...formData, exercise_type: exerciseType })
  }

  return (
    <div className="card">
      <h2>📝 Personaliza tu práctica</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>🎚️ Nivel de inglés</label>
          <select
            value={formData.level}
            onChange={(e) => setFormData({ ...formData, level: e.target.value })}
          >
            <option value="A1">A1 - Principiante</option>
            <option value="A2">A2 - Elemental</option>
            <option value="B1">B1 - Intermedio</option>
            <option value="B2">B2 - Intermedio Alto</option>
          </select>
        </div>

        <div className="form-group">
          <label>📚 Tema que quieres practicar</label>
          <input
            type="text"
            placeholder="Ej: comida, viajes, negocios, ecommerce..."
            value={formData.topic}
            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            required
          />
        </div>

        <div className="form-group">
          <label>🔢 Número de preguntas</label>
          <select
            value={formData.num_questions}
            onChange={(e) => setFormData({ ...formData, num_questions: parseInt(e.target.value) })}
          >
            <option value="5">5 preguntas</option>
            <option value="10">10 preguntas</option>
            <option value="15">15 preguntas</option>
            <option value="20">20 preguntas</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
          🚀 Generar Práctica con IA
        </button>
      </form>
    </div>
  )
}

export default ExerciseSetup
