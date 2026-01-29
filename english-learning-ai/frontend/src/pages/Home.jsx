import { Link } from 'react-router-dom'
import { Headphones, Mic, BookOpen, PenTool } from 'lucide-react'

function Home() {
  return (
    <div>
      <div style={styles.hero}>
        <h1 style={styles.title}>🎯 English Learning AI</h1>
        <p style={styles.subtitle}>
          Tu tutor personal de inglés con inteligencia artificial
        </p>
      </div>

      <div style={styles.grid}>
        <Link to="/listening" style={styles.card}>
          <Headphones size={48} color="#667eea" />
          <h3>Listening</h3>
          <p>Practica comprensión auditiva con ejercicios personalizados</p>
        </Link>

        <Link to="/speaking" style={styles.card}>
          <Mic size={48} color="#667eea" />
          <h3>Speaking</h3>
          <p>Mejora tu pronunciación con evaluación en tiempo real</p>
        </Link>

        <div style={{ ...styles.card, opacity: 0.6 }}>
          <BookOpen size={48} color="#667eea" />
          <h3>Reading</h3>
          <p>Próximamente</p>
        </div>

        <div style={{ ...styles.card, opacity: 0.6 }}>
          <PenTool size={48} color="#667eea" />
          <h3>Grammar</h3>
          <p>Próximamente</p>
        </div>
      </div>

      <div className="card" style={{ marginTop: '3rem' }}>
        <h2>✨ Características</h2>
        <ul style={styles.features}>
          <li>🎯 Ejercicios personalizados por tema y nivel</li>
          <li>🔊 Audio generado con IA de alta calidad</li>
          <li>🎤 Evaluación de pronunciación en tiempo real</li>
          <li>📊 Seguimiento de tu progreso</li>
          <li>🔄 Contenido siempre diferente y único</li>
          <li>⚡ Disponible 24/7 cuando lo necesites</li>
        </ul>
      </div>
    </div>
  )
}

const styles = {
  hero: {
    textAlign: 'center',
    padding: '3rem 0'
  },
  title: {
    fontSize: '3rem',
    marginBottom: '1rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent'
  },
  subtitle: {
    fontSize: '1.5rem',
    color: '#718096'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '2rem',
    marginTop: '3rem'
  },
  card: {
    background: 'white',
    padding: '2rem',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.07)',
    textAlign: 'center',
    textDecoration: 'none',
    color: 'inherit',
    transition: 'transform 0.3s',
    cursor: 'pointer'
  },
  features: {
    listStyle: 'none',
    fontSize: '1.1rem',
    lineHeight: '2'
  }
}

export default Home
